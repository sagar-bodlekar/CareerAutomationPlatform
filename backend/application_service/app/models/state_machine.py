"""Application state machine with valid transitions."""

from typing import Optional


class ApplicationStateMachine:
    """Validates and manages application state transitions.

    States: draft, matched, resume_generated, cover_letter_generated,
            email_prepared, sent, delivered, opened, replied,
            interview_scheduled, offer_received, rejected, withdrawn
    """

    VALID_STATES = [
        "draft", "matched", "resume_generated", "cover_letter_generated",
        "email_prepared", "sent", "delivered", "opened", "replied",
        "interview_scheduled", "offer_received", "rejected", "withdrawn",
    ]

    INITIAL_STATE = "draft"
    TERMINAL_STATES = ["rejected", "withdrawn", "offer_received"]

    # Valid transitions: current_state -> set of allowed next states
    TRANSITIONS: dict[str, set[str]] = {
        "draft": {"matched", "resume_generated", "withdrawn"},
        "matched": {"resume_generated", "cover_letter_generated", "email_prepared", "withdrawn"},
        "resume_generated": {"cover_letter_generated", "email_prepared", "sent", "withdrawn"},
        "cover_letter_generated": {"email_prepared", "sent", "withdrawn"},
        "email_prepared": {"sent", "withdrawn"},
        "sent": {"delivered", "opened", "replied", "bounced", "rejected"},
        "delivered": {"opened", "replied", "rejected"},
        "opened": {"replied", "interview_scheduled", "rejected"},
        "replied": {"interview_scheduled", "rejected"},
        "interview_scheduled": {"offer_received", "rejected", "withdrawn"},
        "offer_received": {"rejected", "withdrawn"},
        "rejected": set(),
        "withdrawn": set(),
    }

    @classmethod
    def is_valid_state(cls, state: str) -> bool:
        """Check if a state is valid."""
        return state in cls.VALID_STATES

    @classmethod
    def is_terminal(cls, state: str) -> bool:
        """Check if a state is terminal (no further transitions)."""
        return state in cls.TERMINAL_STATES

    @classmethod
    def can_transition(cls, current: str, next_state: str) -> bool:
        """Check if a transition is valid."""
        if not cls.is_valid_state(current) or not cls.is_valid_state(next_state):
            return False
        return next_state in cls.TRANSITIONS.get(current, set())

    @classmethod
    def get_allowed_transitions(cls, current: str) -> list[str]:
        """Get all allowed next states from current state."""
        allowed = cls.TRANSITIONS.get(current, set())
        if current in cls.TERMINAL_STATES:
            # Allow manual override from terminal states
            allowed = allowed | {"rejected", "withdrawn"}
        return sorted(allowed)

    @classmethod
    def get_state_display(cls, state: str) -> str:
        """Get a human-readable display name for a state."""
        display_map = {
            "draft": "Draft",
            "matched": "Matched to Job",
            "resume_generated": "Resume Generated",
            "cover_letter_generated": "Cover Letter Generated",
            "email_prepared": "Email Prepared",
            "sent": "Sent",
            "delivered": "Delivered",
            "opened": "Opened by Recipient",
            "replied": "Replied",
            "interview_scheduled": "Interview Scheduled",
            "offer_received": "Offer Received",
            "rejected": "Rejected",
            "withdrawn": "Withdrawn",
        }
        return display_map.get(state, state.replace("_", " ").title())

    @classmethod
    def get_progress_percentage(cls, state: str) -> int:
        """Get progress percentage for a state (for UI display)."""
        progress = {
            "draft": 0,
            "matched": 10,
            "resume_generated": 20,
            "cover_letter_generated": 30,
            "email_prepared": 40,
            "sent": 50,
            "delivered": 60,
            "opened": 70,
            "replied": 75,
            "interview_scheduled": 85,
            "offer_received": 95,
            "rejected": 100,
            "withdrawn": 100,
        }
        return progress.get(state, 0)
