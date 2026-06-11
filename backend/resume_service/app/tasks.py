"""Celery task stubs for async resume processing.

Full integration with Celery worker will be configured in Phase 10.
"""

# import uuid
# from app.services.pdf_generator import PDFGenerator
# from app.services.ats.optimizer import ATSOptimizer


async def generate_resume(resume_id: str, profile_data: dict) -> None:
    """Generate a resume PDF asynchronously.

    Stub: Wires to Celery in Phase 10.
    """
    pass


async def optimize_resume_ats(resume_id: str, job_description: str) -> None:
    """Run ATS optimization asynchronously.

    Stub: Wires to Celery in Phase 10.
    """
    pass
