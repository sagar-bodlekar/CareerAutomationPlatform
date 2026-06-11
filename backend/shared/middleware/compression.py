"""Response compression middleware for FastAPI applications using gzip."""

import logging
from typing import Optional

from fastapi import FastAPI, Response
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class CompressionMiddleware:
    """Compresses response bodies using gzip when client supports it.

    Only compresses responses larger than minimum_size bytes.
    Skips already compressed content types.
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,  # bytes
        compress_level: int = 6,  # 1-9, default 6
    ):
        self.app = app
        self.minimum_size = minimum_size
        self.compress_level = compress_level
        self.skip_content_types = {
            "image/",
            "video/",
            "audio/",
            "application/pdf",
            "application/zip",
            "application/gzip",
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Check if client accepts gzip
        headers = dict(scope.get("headers", []))
        accept_encoding = headers.get(b"accept-encoding", b"").decode()
        if "gzip" not in accept_encoding:
            return await self.app(scope, receive, send)

        # Skip for /metrics and /health
        path = scope.get("path", "/unknown")
        if path in ("/metrics", "/health"):
            return await self.app(scope, receive, send)

        body_chunks = []
        content_type = ""

        async def capture_send(message):
            nonlocal content_type
            if message["type"] == "http.response.start":
                content_type = ""
                for key, value in message.get("headers", []):
                    if key == b"content-type":
                        content_type = value.decode()
                        break

                # Skip compression for certain content types
                for skip in self.skip_content_types:
                    if content_type.startswith(skip):
                        return await send(message)

            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body and len(body) >= self.minimum_size:
                    body_chunks.append(body)
                else:
                    return await send(message)

                more_body = message.get("more_body", False)
                if not more_body:
                    # Compress
                    try:
                        import gzip
                        compressed = gzip.compress(b"".join(body_chunks), self.compress_level)
                        new_headers = [
                            (k, v) for k, v in message.get("headers", [])
                            if k.lower() not in (b"content-length",)
                        ]
                        new_headers.append((b"content-encoding", b"gzip"))
                        new_headers.append((b"content-length", str(len(compressed)).encode()))

                        await send({
                            "type": "http.response.body",
                            "body": compressed,
                            "more_body": False,
                            "headers": new_headers,
                        })
                    except Exception as e:
                        logger.warning("Compression failed: %s", e)
                        await send(message)
                else:
                    body_chunks.append(body)

        await self.app(scope, receive, capture_send)
