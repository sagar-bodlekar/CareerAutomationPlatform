"""Export service for CSV/JSON application data export."""

import csv
import io
import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting application data as CSV or JSON."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_csv(self, profile_id: str) -> str:
        """Export applications as CSV string."""
        from ..models.models import Application

        result = await self.db.execute(
            select(Application).where(Application.profile_id == profile_id)
        )
        apps = list(result.scalars().all())

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Job Title", "Company", "Status", "Match Score",
            "Sent At", "Delivery Status", "Created At", "Updated At",
        ])

        for app in apps:
            writer.writerow([
                app.id,
                app.job_title or "",
                app.company_name or "",
                app.status or "",
                app.match_score or "",
                app.sent_at.isoformat() if app.sent_at else "",
                app.delivery_status or "",
                app.created_at.isoformat() if app.created_at else "",
                app.updated_at.isoformat() if app.updated_at else "",
            ])

        return output.getvalue()

    async def export_json(self, profile_id: str) -> str:
        """Export applications as JSON string."""
        from ..models.models import Application

        result = await self.db.execute(
            select(Application).where(Application.profile_id == profile_id)
        )
        apps = list(result.scalars().all())

        data = []
        for app in apps:
            data.append({
                "id": app.id,
                "job_title": app.job_title,
                "company_name": app.company_name,
                "status": app.status,
                "match_score": app.match_score,
                "sent_at": app.sent_at.isoformat() if app.sent_at else None,
                "delivery_status": app.delivery_status,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None,
            })

        return json.dumps(data, indent=2)
