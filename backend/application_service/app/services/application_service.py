"""Application service CRUD and state management."""

import logging
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Application, ApplicationEvent
from ..models.state_machine import ApplicationStateMachine
from ..schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from .event_service import EventService
from .package_assembler import PackageAssembler
from .state_machine import StateMachineService

logger = logging.getLogger(__name__)


class ApplicationService:
    """Service for application CRUD and state management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.state_machine = StateMachineService(db)
        self.event_service = EventService(db)
        self.package_assembler = PackageAssembler(db)

    async def create(self, data: ApplicationCreate) -> Application:
        """Create a new application draft."""
        application = Application(
            profile_id=data.profile_id,
            job_id=data.job_id,
            user_id=data.user_id,
            company_name=data.company_name,
            job_title=data.job_title,
            job_location=data.job_location,
            job_url=data.job_url,
            match_score=data.match_score,
            match_id=data.match_id,
            notes=data.notes,
            status=ApplicationStateMachine.INITIAL_STATE,
        )
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)

        await self.event_service.create_event(
            application_id=application.id,
            to_status=application.status,
            event_type="created",
            description="Application draft created",
            actor="user",
        )
        return application

    async def get(self, application_id: int) -> Optional[ApplicationResponse]:
        """Get an application with state info."""
        result = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            return None
        return self._to_response(app)

    async def update(self, application_id: int, data: ApplicationUpdate) -> Optional[ApplicationResponse]:
        """Update application fields."""
        result = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            return None

        update_data = data.model_dump(exclude_unset=True)
        new_status = update_data.pop("status", None)

        if new_status:
            valid, error = self.state_machine.validate_transition(app.status, new_status)
            if not valid:
                raise ValueError(error)
            app.previous_status = app.status
            app.status = new_status
            await self.event_service.create_event(
                application_id=app.id,
                to_status=new_status,
                from_status=app.previous_status,
                event_type="status_change",
                description=f"Status changed from {app.previous_status} to {new_status}",
                actor="user",
            )

        for key, value in update_data.items():
            setattr(app, key, value)

        await self.db.flush()
        await self.db.refresh(app)
        return self._to_response(app)

    async def list_applications(
        self, profile_id: int, page: int = 1, per_page: int = 20,
        status: Optional[str] = None,
    ) -> tuple[list[ApplicationResponse], int]:
        """List applications for a profile with pagination."""
        query = select(Application).where(Application.profile_id == profile_id)
        if status:
            query = query.where(Application.status == status)
        query = query.order_by(desc(Application.updated_at))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        result = await self.db.execute(query)
        apps = list(result.scalars().all())

        return [self._to_response(a) for a in apps], total

    async def submit(self, application_id: int) -> Optional[ApplicationResponse]:
        """Submit an application (transition to sent state)."""
        result = await self.db.execute(
            select(Application).where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            return None

        valid, error = self.state_machine.validate_transition(app.status, "sent")
        if not valid:
            raise ValueError(error)

        # Assemble package
        package = await self.package_assembler.assemble(app)
        app.package_data = package

        app.previous_status = app.status
        app.status = "sent"
        app.sent_at = func.now()

        await self.event_service.create_event(
            application_id=app.id,
            to_status="sent",
            from_status=app.previous_status,
            event_type="submitted",
            description="Application submitted",
            actor="user",
        )
        await self.db.flush()
        await self.db.refresh(app)
        return self._to_response(app)

    async def get_events(self, application_id: int) -> list[ApplicationEvent]:
        """Get events/timeline for an application."""
        return await self.event_service.get_events(application_id)

    def _to_response(self, app: Application) -> ApplicationResponse:
        """Convert Application model to response with state info."""
        return ApplicationResponse(
            id=app.id,
            profile_id=app.profile_id,
            job_id=app.job_id,
            user_id=app.user_id,
            status=app.status,
            company_name=app.company_name,
            job_title=app.job_title,
            job_location=app.job_location,
            match_score=app.match_score,
            resume_id=app.resume_id,
            cover_letter_id=app.cover_letter_id,
            email_id=app.email_id,
            delivery_status=app.delivery_status,
            sent_at=app.sent_at,
            retry_count=app.retry_count,
            notes=app.notes,
            created_at=app.created_at,
            updated_at=app.updated_at,
            allowed_transitions=self.state_machine.get_allowed_transitions(app.status),
            progress_percentage=self.state_machine.get_progress(app.status),
        )
