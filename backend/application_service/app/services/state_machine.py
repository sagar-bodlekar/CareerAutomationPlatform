"""State machine service for application transitions."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.state_machine import ApplicationStateMachine

logger = logging.getLogger(__name__)


class StateMachineService:
    """Service for managing application state transitions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def validate_transition(self, current_status: str, new_status: str) -> tuple[bool, Optional[str]]:
        """Validate a state transition.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not ApplicationStateMachine.is_valid_state(new_status):
            return False, f"Invalid state: {new_status}"

        if current_status == new_status:
            return False, f"Already in state: {new_status}"

        if ApplicationStateMachine.can_transition(current_status, new_status):
            return True, None

        allowed = ApplicationStateMachine.get_allowed_transitions(current_status)
        return False, f"Cannot transition from '{current_status}' to '{new_status}'. Allowed: {', '.join(allowed) or 'none (terminal state)'}"

    def get_allowed_transitions(self, current_status: str) -> list[str]:
        """Get allowed next states."""
        return ApplicationStateMachine.get_allowed_transitions(current_status)

    def get_progress(self, status: str) -> int:
        """Get progress percentage for UI."""
        return ApplicationStateMachine.get_progress_percentage(status)
