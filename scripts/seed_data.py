"""Seed script for development sample data.

Populates all services with realistic sample data for testing.
Run with: python scripts/seed_data.py

Requires PostgreSQL and Alembic migrations to be run first.
Infrastructure: docker compose up -d postgres redis minio pgbouncer
Migrations: cd backend && alembic upgrade head
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from shared.config import settings

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─── Sample Data ─────────────────────────────────────────────────


def _now():
    return datetime.now(timezone.utc)


def _days_ago(n):
    return _now() - timedelta(days=n)


async def check_connection(db: AsyncSession) -> bool:
    """Check database connectivity."""
    try:
        result = await db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:
        logger.error("Database connection failed: %s", e)
        return False


async def seed_profile(db: AsyncSession) -> int:
    """Insert sample profile data."""
    from profile_service.app.models.models import (
        UserProfile,
        PersonalInfo,
        Skill,
        WorkExperience,
        Education,
        Project,
    )

    # Check if profile already exists
    result = await db.execute(select(UserProfile).limit(1))
    existing = result.scalar_one_or_none()
    if existing:
        logger.info("Profile already seeded (id=%s), skipping", existing.id)
        return existing.id

    profile = UserProfile(user_id=1, is_active=True, metadata_json={"source": "seed"})
    db.add(profile)
    await db.flush()

    personal_info = PersonalInfo(
        profile_id=profile.id,
        full_name="Alex Johnson",
        email="alex.johnson@example.com",
        phone="+1-555-0123",
        location="San Francisco, CA",
        linkedin_url="https://linkedin.com/in/alexjohnson",
        github_url="https://github.com/alexjohnson",
        portfolio_url="https://alexjohnson.dev",
        title="Senior Full-Stack Engineer",
        summary="Senior full-stack engineer with 8+ years of experience building scalable web applications. "
        "Proficient in Python, TypeScript, React, and cloud infrastructure. "
        "Passionate about AI-assisted development and developer tooling.",
    )
    db.add(personal_info)

    skills_data = [
        ("Python", "expert", "Programming", 5),
        ("TypeScript", "advanced", "Programming", 4),
        ("React", "advanced", "Frontend", 4),
        ("FastAPI", "advanced", "Backend", 4),
        ("PostgreSQL", "advanced", "Database", 4),
        ("Docker", "intermediate", "DevOps", 3),
        ("Kubernetes", "intermediate", "DevOps", 3),
        ("AWS", "advanced", "Cloud", 4),
        ("GraphQL", "intermediate", "API", 3),
        ("Redis", "intermediate", "Database", 3),
        ("Machine Learning", "beginner", "AI", 2),
        ("CI/CD", "advanced", "DevOps", 4),
    ]
    for name, prof, cat, years in skills_data:
        db.add(Skill(profile_id=profile.id, name=name, proficiency=prof, category=cat, years_of_experience=years))

    experiences_data = [
        {
            "company": "TechCorp Inc.",
            "role": "Senior Software Engineer",
            "start": _days_ago(1095),
            "end": None,
            "description": "Led a team of 5 engineers building the core platform. "
            "Architected microservices migration reducing deploy times by 80%. "
            "Implemented real-time collaboration features serving 100K+ users.",
            "location": "San Francisco, CA",
            "is_current": True,
        },
        {
            "company": "StartupXYZ",
            "role": "Full-Stack Developer",
            "start": _days_ago(1825),
            "end": _days_ago(1095),
            "description": "Built customer-facing dashboard from scratch using React + Node.js. "
            "Designed RESTful APIs serving 50K+ daily active users. "
            "Reduced infrastructure costs by 40% through optimization.",
            "location": "Remote",
            "is_current": False,
        },
        {
            "company": "WebAgency Co.",
            "role": "Junior Developer",
            "start": _days_ago(2920),
            "end": _days_ago(1825),
            "description": "Developed responsive web applications for 15+ clients. "
            "Built reusable component library adopted across the organization.",
            "location": "New York, NY",
            "is_current": False,
        },
    ]
    for exp in experiences_data:
        db.add(
            WorkExperience(
                profile_id=profile.id,
                company=exp["company"],
                role=exp["role"],
                start_date=exp["start"],
                end_date=exp["end"],
                description=exp["description"],
                location=exp["location"],
                is_current=exp["is_current"],
            )
        )

    education_data = [
        {
            "institution": "University of California, Berkeley",
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "start": datetime(2014, 9, 1, tzinfo=timezone.utc),
            "end": datetime(2018, 6, 1, tzinfo=timezone.utc),
            "gpa": 3.8,
        },
    ]
    for edu in education_data:
        db.add(
            Education(
                profile_id=profile.id,
                institution=edu["institution"],
                degree=edu["degree"],
                field_of_study=edu["field"],
                start_date=edu["start"],
                end_date=edu["end"],
                gpa=edu["gpa"],
            )
        )

    projects_data = [
        {
            "name": "AI Career Platform",
            "description": "Full-stack career automation platform with AI-powered resume generation, job matching, and application tracking.",
            "url": "https://github.com/example/career-platform",
            "technologies": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        },
        {
            "name": "DevOps Dashboard",
            "description": "Real-time monitoring dashboard for Kubernetes clusters with alerting and metrics visualization.",
            "url": "https://github.com/example/devops-dashboard",
            "technologies": ["Go", "React", "Prometheus", "Grafana", "Kubernetes"],
        },
    ]
    for proj in projects_data:
        db.add(
            Project(
                profile_id=profile.id,
                name=proj["name"],
                description=proj["description"],
                url=proj["url"],
                technologies=proj["technologies"],
            )
        )

    await db.flush()
    logger.info("Seeded profile id=%d with personal info, %d skills, %d experiences, %d education, %d projects",
                profile.id, len(skills_data), len(experiences_data), len(education_data), len(projects_data))
    return profile.id


async def seed_jobs(db: AsyncSession) -> list[int]:
    """Insert sample job listings."""
    from job_service.app.models.models import Job

    result = await db.execute(select(Job).limit(1))
    if result.scalar_one_or_none():
        logger.info("Jobs already seeded, skipping")
        result = await db.execute(select(Job.id))
        return [r[0] for r in result.all()]

    jobs_data = [
        {
            "title": "Senior Software Engineer",
            "company": "Google",
            "location": "Mountain View, CA",
            "remote": False,
            "description": "Build the next generation of Google's cloud infrastructure. "
            "Work on distributed systems serving billions of users. "
            "Required: 5+ years experience with large-scale systems.",
            "required_skills": ["Python", "Go", "Distributed Systems", "Kubernetes", "System Design"],
            "salary_min": 180000,
            "salary_max": 280000,
            "currency": "USD",
            "experience_level": "senior",
            "employment_type": "full-time",
            "url": "https://google.com/careers/123",
            "source": "google_careers",
        },
        {
            "title": "Full-Stack Engineer",
            "company": "Stripe",
            "location": "San Francisco, CA",
            "remote": True,
            "description": "Build developer tools and APIs that power online commerce. "
            "Own features end-to-end from design to deployment. "
            "Strong product sense and user empathy required.",
            "required_skills": ["Ruby", "JavaScript", "React", "PostgreSQL", "API Design"],
            "salary_min": 160000,
            "salary_max": 250000,
            "currency": "USD",
            "experience_level": "mid",
            "employment_type": "full-time",
            "url": "https://stripe.com/jobs/456",
            "source": "stripe_careers",
        },
        {
            "title": "AI/ML Engineer",
            "company": "Anthropic",
            "location": "San Francisco, CA",
            "remote": False,
            "description": "Research and develop safe AI systems. "
            "Work with cutting-edge language models and RLHF. "
            "Published research in ML/NLP preferred.",
            "required_skills": ["Python", "PyTorch", "NLP", "Machine Learning", "Transformers"],
            "salary_min": 200000,
            "salary_max": 350000,
            "currency": "USD",
            "experience_level": "senior",
            "employment_type": "full-time",
            "url": "https://anthropic.com/careers/789",
            "source": "anthropic_careers",
        },
        {
            "title": "Backend Engineer",
            "company": "Datadog",
            "location": "New York, NY",
            "remote": True,
            "description": "Build observability infrastructure at massive scale. "
            "Design and implement high-throughput data pipelines. "
            "Experience with time-series databases a plus.",
            "required_skills": ["Go", "Java", "Kafka", "Cassandra", "Distributed Systems"],
            "salary_min": 150000,
            "salary_max": 240000,
            "currency": "USD",
            "experience_level": "mid",
            "employment_type": "full-time",
            "url": "https://datadog.com/jobs/101",
            "source": "datadog_careers",
        },
        {
            "title": "Frontend Engineer",
            "company": "Figma",
            "location": "San Francisco, CA",
            "remote": True,
            "description": "Build real-time collaborative design tools. "
            "Push the boundaries of what's possible in the browser. "
            "Deep expertise in web rendering and Canvas/WebGL.",
            "required_skills": ["TypeScript", "React", "WebGL", "Canvas", "WebAssembly"],
            "salary_min": 160000,
            "salary_max": 260000,
            "currency": "USD",
            "experience_level": "mid",
            "employment_type": "full-time",
            "url": "https://figma.com/careers/202",
            "source": "figma_careers",
        },
        {
            "title": "DevOps Engineer",
            "company": "Netflix",
            "location": "Los Gatos, CA",
            "remote": False,
            "description": "Build and operate the streaming platform infrastructure. "
            "Design chaos engineering experiments. "
            "Automate everything mindset required.",
            "required_skills": ["AWS", "Terraform", "Kubernetes", "Python", "Chaos Engineering"],
            "salary_min": 170000,
            "salary_max": 290000,
            "currency": "USD",
            "experience_level": "senior",
            "employment_type": "full-time",
            "url": "https://netflix.com/jobs/303",
            "source": "netflix_careers",
        },
    ]

    job_ids = []
    for job_data in jobs_data:
        job = Job(**job_data)
        db.add(job)
        await db.flush()
        job_ids.append(job.id)

    logger.info("Seeded %d jobs", len(jobs_data))
    return job_ids


async def seed_resumes(db: AsyncSession, profile_id: int) -> int:
    """Insert sample resume."""
    from resume_service.app.models.models import Resume

    result = await db.execute(select(Resume).limit(1))
    if result.scalar_one_or_none():
        logger.info("Resume already seeded, skipping")
        result = await db.execute(select(Resume.id))
        return result.scalar()

    resume = Resume(
        profile_id=profile_id,
        title="Master Resume",
        template="modern",
        content={
            "sections": [
                {"type": "summary", "content": "Senior full-stack engineer with 8+ years of experience..."},
                {"type": "experience", "content": "See work experience section"},
                {"type": "education", "content": "UC Berkeley, B.S. Computer Science"},
                {"type": "skills", "content": "Python, TypeScript, React, FastAPI, PostgreSQL, AWS"},
            ]
        },
        ats_score=85,
        version=1,
    )
    db.add(resume)
    await db.flush()
    logger.info("Seeded resume id=%d", resume.id)
    return resume.id


async def seed_application(db: AsyncSession, profile_id: int, job_ids: list[int]) -> int:
    """Insert sample application with events."""
    from application_service.app.models.models import Application, ApplicationEvent

    result = await db.execute(select(Application).limit(1))
    if result.scalar_one_or_none():
        logger.info("Application already seeded, skipping")
        return (await db.execute(select(Application.id))).scalar()

    app = Application(
        profile_id=profile_id,
        job_id=job_ids[0],
        user_id=1,
        status="sent",
        previous_status="draft",
        company_name="Google",
        job_title="Senior Software Engineer",
        job_location="Mountain View, CA",
        job_url="https://google.com/careers/123",
        match_score=82.5,
        sent_at=_days_ago(7),
        delivery_status="delivered",
        delivery_message_id="smtp-msg-001",
        notes="Strong match based on cloud infrastructure experience",
        metadata_json={"source": "seed", "priority": "high"},
    )
    db.add(app)
    await db.flush()

    events_data = [
        ("draft", "matched", "status_change", "Profile matched to job", _days_ago(10)),
        ("matched", "resume_generated", "status_change", "Resume generated for Google application", _days_ago(9)),
        ("resume_generated", "cover_letter_generated", "status_change", "Cover letter generated", _days_ago(9)),
        ("cover_letter_generated", "email_prepared", "status_change", "Email prepared for delivery", _days_ago(8)),
        ("email_prepared", "sent", "email_sent", "Application sent via SMTP", _days_ago(7)),
        ("sent", "sent", "email_delivered", "Email delivered to recipient", _days_ago(6)),
    ]
    for from_status, to_status, event_type, desc, timestamp in events_data:
        db.add(
            ApplicationEvent(
                application_id=app.id,
                from_status=from_status,
                to_status=to_status,
                event_type=event_type,
                description=desc,
                actor="system",
                metadata_json={"timestamp": timestamp.isoformat()},
                created_at=timestamp,
            )
        )

    # Add a second application
    app2 = Application(
        profile_id=profile_id,
        job_id=job_ids[1],
        user_id=1,
        status="draft",
        company_name="Stripe",
        job_title="Full-Stack Engineer",
        job_location="San Francisco, CA",
        match_score=75.0,
        delivery_status="pending",
        notes="Good skill match, needs cover letter",
        metadata_json={"source": "seed"},
    )
    db.add(app2)
    await db.flush()

    await db.flush()
    logger.info("Seeded application id=%d with %d events, plus draft application id=%d",
                app.id, len(events_data), app2.id)
    return app.id


async def seed_tracking(db: AsyncSession, profile_id: int):
    """Insert sample tracking stats."""
    from tracking_service.app.models.models import ApplicationStat, ApplicationFunnel, DailyCount

    result = await db.execute(select(ApplicationStat).limit(1))
    if result.scalar_one_or_none():
        logger.info("Tracking stats already seeded, skipping")
        return

    stat = ApplicationStat(
        profile_id=profile_id,
        total_applications=28,
        total_sent=24,
        total_delivered=22,
        total_opened=18,
        total_replied=12,
        total_interviews=6,
        total_offers=2,
        total_rejected=3,
        avg_match_score=78.5,
        avg_response_time_hours=48.0,
        success_rate=25.0,
        last_activity_at=_days_ago(1),
    )
    db.add(stat)

    funnel = ApplicationFunnel(
        profile_id=profile_id,
        status_counts={
            "draft": 4, "matched": 2, "resume_generated": 1, "sent": 6,
            "delivered": 4, "opened": 5, "replied": 3, "interview_scheduled": 2,
            "offer_received": 1, "rejected": 2, "withdrawn": 1,
        },
    )
    db.add(funnel)

    for i in range(30):
        db.add(DailyCount(
            profile_id=profile_id,
            date=_days_ago(29 - i),
            count=1 if i % 3 == 0 else 0,
            sent_count=1,
        ))

    await db.flush()
    logger.info("Seeded tracking stats for profile %d", profile_id)


async def seed_outreach(db: AsyncSession, profile_id: int):
    """Insert sample outreach content."""
    from outreach_service.app.models.models import OutreachContent

    result = await db.execute(select(OutreachContent).limit(1))
    if result.scalar_one_or_none():
        logger.info("Outreach content already seeded, skipping")
        return

    content = OutreachContent(
        profile_id=profile_id,
        content_type="cover_letter",
        tone="professional",
        content_text="Dear Hiring Manager,\n\n"
        "I am writing to express my strong interest in the Senior Software Engineer "
        "position at Google. With over 8 years of experience building large-scale "
        "distributed systems, I am confident that my technical expertise and passion "
        "for innovation would make me a valuable addition to your team.\n\n"
        "At TechCorp Inc., I led a team of 5 engineers in migrating our monolithic "
        "architecture to microservices, resulting in 80% faster deployments. "
        "I have extensive experience with Python, Go, and Kubernetes, which I "
        "understand are central to Google's infrastructure.\n\n"
        "I would welcome the opportunity to discuss how my experience aligns with "
        "Google's needs. Thank you for your consideration.\n\n"
        "Best regards,\nAlex Johnson",
        metadata_json={"job_title": "Senior Software Engineer", "company": "Google"},
        version=1,
    )
    db.add(content)
    await db.flush()
    logger.info("Seeded outreach content id=%d", content.id)


async def seed_match(db: AsyncSession, profile_id: int, job_ids: list[int]):
    """Insert sample match data."""
    from match_service.app.models.models import JobMatch

    result = await db.execute(select(JobMatch).limit(1))
    if result.scalar_one_or_none():
        logger.info("Matches already seeded, skipping")
        return

    matches_data = [
        (job_ids[0], 82.5, {"skills": 85, "experience": 80, "education": 75, "title": 90}),
        (job_ids[1], 75.0, {"skills": 80, "experience": 70, "education": 75, "title": 75}),
        (job_ids[2], 45.0, {"skills": 50, "experience": 60, "education": 70, "title": 30}),
        (job_ids[3], 70.0, {"skills": 75, "experience": 85, "education": 75, "title": 60}),
        (job_ids[4], 78.0, {"skills": 85, "experience": 70, "education": 75, "title": 80}),
        (job_ids[5], 65.0, {"skills": 60, "experience": 75, "education": 70, "title": 55}),
    ]
    for job_id, score, breakdown in matches_data:
        db.add(JobMatch(
            profile_id=profile_id,
            job_id=job_id,
            overall_score=score,
            skills_score=breakdown["skills"],
            experience_score=breakdown["experience"],
            education_score=breakdown["education"],
            title_score=breakdown["title"],
            match_data={"computed_at": _now().isoformat()},
        ))

    await db.flush()
    logger.info("Seeded %d matches for profile %d", len(matches_data), profile_id)


async def seed_all():
    """Run all seed functions in order."""
    engine = create_async_engine(settings.db_url)
    async with sessionmaker(engine, class_=AsyncSession)() as db:
        if not await check_connection(db):
            logger.error("Cannot connect to database. Is PostgreSQL running?")
            logger.info("Start with: docker compose up -d postgres")
            logger.info("Run migrations: cd backend && alembic upgrade head")
            return False

        logger.info("Connected to database: %s", settings.postgres_db)

        # Seed in dependency order
        profile_id = await seed_profile(db)
        job_ids = await seed_jobs(db)
        resume_id = await seed_resumes(db, profile_id)
        app_id = await seed_application(db, profile_id, job_ids)
        await seed_tracking(db, profile_id)
        await seed_outreach(db, profile_id)
        await seed_match(db, profile_id, job_ids)

        await db.commit()
        logger.info("=" * 50)
        logger.info("Database seeded successfully!")
        logger.info("Profile ID: %d", profile_id)
        logger.info("Jobs seeded: %d", len(job_ids))
        logger.info("Resume ID: %d", resume_id)
        logger.info("Application IDs: %d+", app_id)
        logger.info("=" * 50)
        return True


if __name__ == "__main__":
    success = asyncio.run(seed_all())
    if not success:
        exit(1)
