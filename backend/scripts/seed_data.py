#!/usr/bin/env python3
"""Seed the database with sample development data.

Usage:
    python backend/scripts/seed_data.py

Requires:
    - PostgreSQL running with migrations applied
    - Environment variables in .env or set in environment
"""

import asyncio
import sys
from datetime import date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import async_session_factory, engine
from shared.logging import get_logger, setup_logging

logger = get_logger(__name__)


async def check_connection() -> bool:
    """Verify database connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False


async def seed_sample_profile(session: AsyncSession) -> str:
    """Create a sample user profile with personal info, skills, and experience."""
    profile_id = str(uuid4())
    user_id = str(uuid4())

    # Insert auth user (dummy for dev) — only if table exists (Phase 3+)
    result = await session.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'career' AND table_name = 'auth_users'
            )
        """)
    )
    if result.scalar():
        await session.execute(
            text("""
                INSERT INTO career.auth_users (id, email, password_hash, is_verified, is_active)
                VALUES (:id, :email, :password_hash, :is_verified, :is_active)
                ON CONFLICT (email) DO NOTHING
            """),
            {
                "id": user_id,
                "email": "dev@example.com",
                "password_hash": "$2b$12$devplaceholder",
                "is_verified": True,
                "is_active": True,
            },
        )
    else:
        logger.warning("career.auth_users table not found — skipping auth user seed (run Phase 3 migrations)")

    # Insert user profile
    await session.execute(
        text("""
            INSERT INTO career.user_profiles (id, user_id, headline, summary,
                location_city, location_country, location_type, preferred_roles,
                target_salary_min, target_salary_max, target_salary_currency,
                open_to_work, years_of_experience)
            VALUES (:id, :user_id, :headline, :summary,
                :location_city, :location_country, :location_type, :preferred_roles,
                :target_salary_min, :target_salary_max, :target_salary_currency,
                :open_to_work, :years_of_experience)
            ON CONFLICT (id) DO NOTHING
        """),
        {
            "id": profile_id,
            "user_id": user_id,
            "headline": "Senior Full-Stack Developer",
            "summary": "Experienced full-stack developer with 8+ years building scalable web applications with Python, React, and cloud technologies.",
            "location_city": "Bangalore",
            "location_country": "India",
            "location_type": "hybrid",
            "preferred_roles": ["Senior Full-Stack Developer", "Backend Developer", "Tech Lead"],
            "target_salary_min": 2000000,
            "target_salary_max": 4000000,
            "target_salary_currency": "INR",
            "open_to_work": True,
            "years_of_experience": 8.0,
        },
    )

    # Insert personal info
    await session.execute(
        text("""
            INSERT INTO career.personal_info (id, profile_id, full_name, email, phone, city, country)
            VALUES (:id, :profile_id, :full_name, :email, :phone, :city, :country)
            ON CONFLICT (id) DO NOTHING
        """),
        {
            "id": str(uuid4()),
            "profile_id": profile_id,
            "full_name": "Alex Developer",
            "email": "dev@example.com",
            "phone": "+91-9876543210",
            "city": "Bangalore",
            "country": "India",
        },
    )

    # Insert skills
    skills = [
        ("Python", "Language", "expert", 8),
        ("React", "Framework", "advanced", 4),
        ("TypeScript", "Language", "advanced", 4),
        ("PostgreSQL", "Database", "advanced", 4),
        ("Docker", "DevOps", "intermediate", 3),
        ("FastAPI", "Framework", "advanced", 4),
        ("AWS", "Cloud", "intermediate", 3),
        ("GraphQL", "API", "intermediate", 3),
        ("Redis", "Database", "intermediate", 3),
        ("Machine Learning", "AI", "beginner", 1),
    ]
    for skill_name, category, proficiency, years in skills:
        await session.execute(
            text("""
                INSERT INTO career.skills (id, profile_id, name, category, proficiency, years_used, is_top_skill)
                VALUES (:id, :profile_id, :name, :category, :proficiency, :years, :is_top)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": str(uuid4()),
                "profile_id": profile_id,
                "name": skill_name,
                "category": category,
                "proficiency": proficiency,
                "years": years,
                "is_top": proficiency in ("expert", "advanced"),
            },
        )

    # Insert work experience
    experiences = [
        {
            "company": "Tech Corp India",
            "title": "Senior Full-Stack Developer",
            "type": "full_time",
            "start": date(2021, 3, 1),
            "end": None,
            "current": True,
            "description": "Leading full-stack development team building SaaS products. Architected microservices with FastAPI, React frontend, and PostgreSQL.",
            "achievements": [
                "Led migration from monolith to microservices, reducing deployment time by 80%",
                "Designed and implemented real-time notification system handling 1M+ events/day",
                "Mentored 4 junior developers through structured code review program",
            ],
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        },
        {
            "company": "StartupXYZ",
            "title": "Full-Stack Developer",
            "type": "full_time",
            "start": date(2018, 6, 1),
            "end": date(2021, 2, 28),
            "current": False,
            "description": "Built core platform features for B2B marketplace startup. Worked across the full stack from database to frontend.",
            "achievements": [
                "Built RESTful API serving 50K+ daily active users",
                "Implemented search functionality using Elasticsearch, improving discovery by 40%",
                "Reduced page load time by 60% through React performance optimization",
            ],
            "skills": ["Python", "React", "TypeScript", "PostgreSQL"],
        },
        {
            "company": "Web Agency Pro",
            "title": "Junior Developer",
            "type": "full_time",
            "start": date(2016, 1, 1),
            "end": date(2018, 5, 31),
            "current": False,
            "description": "Developed custom web applications for diverse clients across e-commerce, healthcare, and finance sectors.",
            "achievements": [
                "Delivered 15+ client projects on time and within budget",
                "Built custom CMS using Django for content-heavy client sites",
                "Implemented CI/CD pipelines reducing deployment errors by 90%",
            ],
            "skills": ["Python", "JavaScript", "PostgreSQL"],
        },
    ]
    for exp in experiences:
        exp_id = str(uuid4())
        await session.execute(
            text("""
                INSERT INTO career.work_experiences
                    (id, profile_id, company_name, job_title, employment_type,
                     start_date, end_date, is_current, description, achievements, skills_used)
                VALUES
                    (:id, :profile_id, :company, :title, :type,
                     :start, :end, :current, :description, :achievements, :skills)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": exp_id,
                "profile_id": profile_id,
                "company": exp["company"],
                "title": exp["title"],
                "type": exp["type"],
                "start": exp["start"],
                "end": exp["end"],
                "current": exp["current"],
                "description": exp["description"],
                "achievements": exp["achievements"],
                "skills": exp["skills"],
            },
        )

    # Insert education
    edu_id = str(uuid4())
    await session.execute(
        text("""
            INSERT INTO career.education (id, profile_id, institution, degree, field_of_study,
                start_date, end_date, grade, description)
            VALUES (:id, :profile_id, :institution, :degree, :field,
                :start, :end, :grade, :description)
            ON CONFLICT DO NOTHING
        """),
        {
            "id": edu_id,
            "profile_id": profile_id,
            "institution": "Indian Institute of Technology",
            "degree": "B.Tech",
            "field": "Computer Science",
            "start": date(2012, 7, 1),
            "end": date(2016, 6, 30),
            "grade": "8.5 CGPA",
            "description": "Bachelor of Technology in Computer Science with focus on algorithms and distributed systems.",
        },
    )

    # Insert social links
    social_links = [
        ("github", "https://github.com/alexdev", "GitHub", True),
        ("linkedin", "https://linkedin.com/in/alexdev", "LinkedIn", False),
        ("portfolio", "https://alexdev.dev", "Portfolio", False),
    ]
    for platform, url, label, is_primary in social_links:
        await session.execute(
            text("""
                INSERT INTO career.social_links (id, profile_id, platform, url, label, is_primary)
                VALUES (:id, :profile_id, :platform, :url, :label, :is_primary)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": str(uuid4()),
                "profile_id": profile_id,
                "platform": platform,
                "url": url,
                "label": label,
                "is_primary": is_primary,
            },
        )

    logger.info("Seed profile created", profile_id=profile_id, user_id=user_id)
    return profile_id


async def seed_sample_jobs(session: AsyncSession) -> list[str]:
    """Create sample job listings."""
    job_ids = []

    # Check if jobs table exists (Phase 5+)
    result = await session.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'career' AND table_name = 'jobs'
            )
        """)
    )
    if not result.scalar():
        logger.warning("career.jobs table not found — skipping job seed (run Phase 5 migrations)")
        return []

    jobs = [
        {
            "title": "Senior Python Backend Developer",
            "company": "TechUnicorn",
            "location": "Bangalore, India",
            "remote": True,
            "salary_min": 2500000,
            "salary_max": 4000000,
            "currency": "INR",
            "description": "Build and maintain high-performance Python microservices serving millions of users.",
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
            "experience_min": 4,
            "experience_max": 8,
            "source": "demo",
            "source_url": "https://example.com/jobs/senior-python-dev",
        },
        {
            "title": "Full Stack Engineer (React + Python)",
            "company": "ProductLabs",
            "location": "Remote",
            "remote": True,
            "salary_min": 2000000,
            "salary_max": 3500000,
            "currency": "INR",
            "description": "Build next-generation collaboration tools. Full ownership from database schema to UI.",
            "required_skills": ["React", "Python", "TypeScript", "PostgreSQL", "GraphQL"],
            "experience_min": 3,
            "experience_max": 7,
            "source": "demo",
            "source_url": "https://example.com/jobs/fullstack-engineer",
        },
        {
            "title": "Backend Engineer - AI/ML Platform",
            "company": "AIFirst",
            "location": "Mumbai, India",
            "remote": False,
            "salary_min": 3000000,
            "salary_max": 5000000,
            "currency": "INR",
            "description": "Build infrastructure powering ML training and inference platform.",
            "required_skills": ["Python", "Machine Learning", "Docker", "Kubernetes", "PostgreSQL"],
            "experience_min": 5,
            "experience_max": 10,
            "source": "demo",
            "source_url": "https://example.com/jobs/ai-ml-engineer",
        },
        {
            "title": "Frontend Lead (React + TypeScript)",
            "company": "DesignStack",
            "location": "Delhi, India",
            "remote": True,
            "salary_min": 2200000,
            "salary_max": 3800000,
            "currency": "INR",
            "description": "Lead frontend architecture for design collaboration platform.",
            "required_skills": ["React", "TypeScript", "GraphQL", "Docker"],
            "experience_min": 4,
            "experience_max": 8,
            "source": "demo",
            "source_url": "https://example.com/jobs/frontend-lead",
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudNative Inc",
            "location": "Remote",
            "remote": True,
            "salary_min": 1800000,
            "salary_max": 3200000,
            "currency": "INR",
            "description": "Design and maintain cloud infrastructure for SaaS platform.",
            "required_skills": ["Docker", "Python", "PostgreSQL", "Redis"],
            "experience_min": 3,
            "experience_max": 7,
            "source": "demo",
            "source_url": "https://example.com/jobs/devops-engineer",
        },
    ]

    for job in jobs:
        job_id = str(uuid4())
        required_skills = job.pop("required_skills")
        await session.execute(
            text("""
                INSERT INTO career.jobs (id, title, company, location, remote,
                    salary_min, salary_max, salary_currency, description,
                    required_skills, experience_min, experience_max,
                    source, source_url, posted_at, expiry_date)
                VALUES (:id, :title, :company, :location, :remote,
                    :salary_min, :salary_max, :salary_currency, :description,
                    :required_skills, :experience_min, :experience_max,
                    :source, :source_url, :posted_at, :expiry_date)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": job_id,
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "remote": job["remote"],
                "salary_min": job["salary_min"],
                "salary_max": job["salary_max"],
                "salary_currency": job["currency"],
                "description": job["description"],
                "required_skills": required_skills,
                "experience_min": job["experience_min"],
                "experience_max": job["experience_max"],
                "source": job["source"],
                "source_url": job["source_url"],
                "posted_at": datetime.utcnow() - timedelta(days=7),
                "expiry_date": datetime.utcnow() + timedelta(days=30),
            },
        )
        job_ids.append(job_id)

    logger.info("Seed jobs created", count=len(job_ids))
    return job_ids


async def main() -> int:
    """Run the seed script."""
    setup_logging()
    logger.info("Starting database seed...")

    if not await check_connection():
        logger.error("Cannot connect to database. Is it running?")
        return 1

    async with async_session_factory() as session:
        try:
            profile_id = await seed_sample_profile(session)
            job_ids = await seed_sample_jobs(session)
            await session.commit()
            logger.info(
                "Seed complete",
                profile_id=profile_id,
                job_count=len(job_ids),
            )
            return 0
        except Exception as e:
            await session.rollback()
            logger.error("Seed failed", error=str(e))
            return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
