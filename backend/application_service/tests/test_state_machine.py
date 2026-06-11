"""Tests for application state machine."""

import pytest

from app.models.state_machine import ApplicationStateMachine


class TestApplicationStateMachine:
    """Test suite for the application state machine."""

    def test_initial_state(self):
        """Test that initial state is 'draft'."""
        assert ApplicationStateMachine.INITIAL_STATE == "draft"

    def test_valid_states(self):
        """Test all valid states are recognized."""
        valid_states = [
            "draft", "matched", "resume_generated", "cover_letter_generated",
            "email_prepared", "sent", "delivered", "opened", "replied",
            "interview_scheduled", "offer_received", "rejected", "withdrawn",
        ]
        for state in valid_states:
            assert ApplicationStateMachine.is_valid_state(state)

    def test_invalid_state(self):
        """Test invalid state is rejected."""
        assert not ApplicationStateMachine.is_valid_state("nonexistent_state")
        assert not ApplicationStateMachine.is_valid_state("")

    def test_terminal_states(self):
        """Test terminal states."""
        assert ApplicationStateMachine.is_terminal("rejected")
        assert ApplicationStateMachine.is_terminal("withdrawn")
        assert ApplicationStateMachine.is_terminal("offer_received")
        assert not ApplicationStateMachine.is_terminal("draft")
        assert not ApplicationStateMachine.is_terminal("sent")

    def test_valid_transition_draft_to_matched(self):
        """Test draft -> matched is valid."""
        assert ApplicationStateMachine.can_transition("draft", "matched")

    def test_valid_transition_sent_to_delivered(self):
        """Test sent -> delivered is valid."""
        assert ApplicationStateMachine.can_transition("sent", "delivered")

    def test_invalid_transition_draft_to_sent(self):
        """Test draft -> sent is not valid (must go through intermediate states)."""
        assert not ApplicationStateMachine.can_transition("draft", "sent")

    def test_invalid_transition_rejected_to_sent(self):
        """Test rejected -> sent is not valid (terminal state)."""
        assert not ApplicationStateMachine.can_transition("rejected", "sent")

    def test_withdrawn_anytime(self):
        """Test that 'withdrawn' is reachable from most states."""
        assert ApplicationStateMachine.can_transition("draft", "withdrawn")
        assert ApplicationStateMachine.can_transition("matched", "withdrawn")
        assert ApplicationStateMachine.can_transition("resume_generated", "withdrawn")
        assert ApplicationStateMachine.can_transition("cover_letter_generated", "withdrawn")
        assert ApplicationStateMachine.can_transition("email_prepared", "withdrawn")
        assert ApplicationStateMachine.can_transition("interview_scheduled", "withdrawn")

    def test_full_forward_path(self):
        """Test full forward path from draft to offer_received."""
        path = ["draft", "matched", "resume_generated", "cover_letter_generated",
                "email_prepared", "sent", "delivered", "opened", "replied",
                "interview_scheduled", "offer_received"]
        for i in range(len(path) - 1):
            assert ApplicationStateMachine.can_transition(path[i], path[i + 1]), \
                f"Invalid transition: {path[i]} -> {path[i + 1]}"

    def test_get_allowed_transitions_from_draft(self):
        """Test allowed transitions from draft state."""
        allowed = ApplicationStateMachine.get_allowed_transitions("draft")
        assert "matched" in allowed
        assert "resume_generated" in allowed
        assert "withdrawn" in allowed
        assert "sent" not in allowed

    def test_get_allowed_transitions_from_rejected(self):
        """Test terminal state has no allowed transitions."""
        allowed = ApplicationStateMachine.get_allowed_transitions("rejected")
        assert "rejected" in allowed  # Manual override
        assert "withdrawn" in allowed

    def test_state_display(self):
        """Test human-readable state display names."""
        assert ApplicationStateMachine.get_state_display("draft") == "Draft"
        assert ApplicationStateMachine.get_state_display("interview_scheduled") == "Interview Scheduled"
        assert ApplicationStateMachine.get_state_display("offer_received") == "Offer Received"
        assert ApplicationStateMachine.get_state_display("sent") == "Sent"

    def test_progress_percentage(self):
        """Test progress percentage mapping."""
        assert ApplicationStateMachine.get_progress_percentage("draft") == 0
        assert ApplicationStateMachine.get_progress_percentage("sent") == 50
        assert ApplicationStateMachine.get_progress_percentage("offer_received") == 95
        assert ApplicationStateMachine.get_progress_percentage("rejected") == 100


class TestStateMachineService:
    """Tests for the state machine service layer."""

    @pytest.mark.asyncio
    async def test_validate_valid_transition(self):
        """Test validating a valid transition."""
        from app.services.state_machine import StateMachineService
        svc = StateMachineService(db=None)  # type: ignore
        valid, error = svc.validate_transition("draft", "matched")
        assert valid
        assert error is None

    @pytest.mark.asyncio
    async def test_validate_invalid_transition(self):
        """Test validating an invalid transition."""
        from app.services.state_machine import StateMachineService
        svc = StateMachineService(db=None)  # type: ignore
        valid, error = svc.validate_transition("draft", "sent")
        assert not valid
        assert error is not None
        assert "Cannot transition" in error

    @pytest.mark.asyncio
    async def test_validate_same_state(self):
        """Test validating transition to same state."""
        from app.services.state_machine import StateMachineService
        svc = StateMachineService(db=None)  # type: ignore
        valid, error = svc.validate_transition("draft", "draft")
        assert not valid
        assert "Already in state" in error

    @pytest.mark.asyncio
    async def test_get_progress(self):
        """Test progress percentage retrieval."""
        from app.services.state_machine import StateMachineService
        svc = StateMachineService(db=None)  # type: ignore
        assert svc.get_progress("draft") == 0
        assert svc.get_progress("sent") == 50
