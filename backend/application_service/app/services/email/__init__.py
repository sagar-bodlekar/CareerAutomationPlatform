"""Email provider abstractions for delivery."""

from .base_provider import EmailProvider, DeliveryResult
from .smtp_provider import SMTPProvider
from .postal_provider import PostalProvider

__all__ = ["EmailProvider", "DeliveryResult", "SMTPProvider", "PostalProvider"]
