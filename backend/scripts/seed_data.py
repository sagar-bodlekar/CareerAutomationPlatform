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
    table_exists = await session.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'career' AND table_name = 'auth_users'
            )
        """)
    )
    if table_exists.scalar():
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
            INSERT INTO career.user_profiles (id, user_id, headline, summary, location, timezone)
            VALUES (:id, :user_id, :headline, :summary, :location, :timezone)
            ON CONFLICT (id) DO NOTHING
        """),
        {
            "id": profile_id,
            "user_id": user_id,
            "headline": "Senior Full-Stack Developer",
            "summary": "Experienced full-stack developer with 8+ years building scalable web applications with Python, React, and cloud technologies.",
            "location": "Bangalore, India",
            "timezone": "Asia/Kolkata",
        },
    )

    # Insert personal info
    await session.execute(
        text("""
            INSERT INTO career.personal_info (id, profile_id, full_name, email, phone, linkedin_url, github_url, portfolio_url)
            VALUES (:id, :profile_id, :full_name, :email, :phone, :linkedin_url, :github_url, :portfolio_url)
            ON CONFLICT (id) DO NOTHING
        """),
        {
            "id": str(uuid4()),
            "profile_id": profile_id,
            "full_name": "Alex Developer",
            "email": "dev@example.com",
            "phone": "+91-9876543210",
            "linkedin_url": "https://linkedin.com/in/alexdev",
            "github_url": "https://github.com/alexdev",
            "portfolio_url": "https://alexdev.dev",
        },
    )

    # Insert skills
    skills = [
        ("Python", "EXPERT", 5),
        ("React", "ADVANCED", 4),
        ("TypeScript", "ADVANCED", 4),
        ("PostgreSQL", "ADVANCED", 4),
        ("Docker", "INTERMEDIATE", 3),
        ("FastAPI", "ADVANCED", 4),
        ("AWS", "INTERMEDIATE", 3),
        ("GraphQL", "INTERMEDIATE", 3),
        ("Redis", "INTERMEDIATE", 3),
        ("Machine Learning", "BEGINNER", 1),
    ]
    for skill_name, proficiency, years in skills:
        await session.execute(
            text("""
                INSERT INTO career.skills (id, profile_id, name, proficiency, years_of_experience)
                VALUES (:id, :profile_id, :name, :proficiency, :years)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": str(uuid4()),
                "profile_id": profile_id,
                "name": skill_name,
                "proficiency": proficiency,
                "years": years,
            },
        )

    # Insert work experience
    experiences = [
        {
            "company": "Tech Corp India",
            "role": "Senior Full-Stack Developer",
            "start": date(2021, 3, 1),
            "end": None,
            "description": "Leading full-stack development team building SaaS products. Architected microservices with FastAPI, React frontend, and PostgreSQL.",
            "highlights": [
                "Led migration from monolith to microservices, reducing deployment time by 80%",
                "Designed and implemented real-time notification system handling 1M+ events/day",
                "Mentored 4 junior developers through structured code review program",
            ],
        },
        {
            "company": "StartupXYZ",
            "role": "Full-Stack Developer",
            "start": date(2018, 6, 1),
            "end": date(2021, 2, 28),
            "description": "Built core platform features for B2B marketplace startup. Worked across the full stack from database to frontend.",
            "highlights": [
                "Built RESTful API serving 50K+ daily active users",
                "Implemented search functionality using Elasticsearch, improving discovery by 40%",
                "Reduced page load time by 60% through React performance optimization",
            ],
        },
        {
            "company": "Web Agency Pro",
            "role": "Junior Developer",
            "start": date(2016, 1, 1),
            "end": date(2018, 5, 31),
            "description": "Developed custom web applications for diverse clients across e-commerce, healthcare, and finance sectors.",
            "highlights": [
                "Delivered 15+ client projects on time and within budget",
                "Built custom CMS using Django for content-heavy client sites",
                "Implemented CI/CD pipelines reducing deployment errors by 90%",
            ],
        },
    ]
    for exp in experiences:
        exp_id = str(uuid4())
        await session.execute(
            text("""
                INSERT INTO career.work_experiences (id, profile_id, company_name, role, start_date, end_date, description, highlights)
                VALUES (:id, :profile_id, :company, :role, :start, :end, :description, :highlights)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": exp_id,
                "profile_id": profile_id,
                "company": exp["company"],
                "role": exp["role"],
                "start": exp["start"],
                "end": exp["end"],
                "description": exp["description"],
                "highlights": exp["highlights"],
            },
        )

    # Insert education
    await session.execute(
        text("""
            INSERT INTO career.education (id, profile_id, institution, degree, field_of_study, start_date, end_date, gpa)
            VALUES (:id, :profile_id, :institution, :degree, :field, :start, :end, :gpa)
            ON CONFLICT DO NOTHING
        """),
        {
            "id": str(uuid4()),
            "profile_id": profile_id,
            "institution": "Indian Institute of Technology",
            "degree": "B.Tech",
            "field": "Computer Science",
            "start": date(2012, 7, 1),
            "end": date(2016, 6, 30),
            "gpa": 8.5,
        },
    )

    logger.info("Seed profile created", profile_id=profile_id, user_id=user_id)
    return profile_id


async def seed_sample_jobs(session: AsyncSession) -> list[str]:
    """Create sample job listings."""
    job_ids = []

    jobs = [
        {
            "title": "Senior Python Backend Developer",
            "company": "TechUnicorn",
            "location": "Bangalore, India",
            "remote": True,
            "salary_min": 2500000,
            "salary_max": 4000000,
            "currency": "INR",
            "description": "Build and maintain high-performance Python microservices serving millions of users. Work with FastAPI, PostgreSQL, Redis, and Kafka.",
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
            "description": "Join our product team to build next-generation collaboration tools. Full ownership from database schema to UI components.",
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
            "description": "Build the infrastructure powering our ML training and inference platform. Experience with distributed systems and GPU clusters preferred.",
            "required_skills": ["Python", "Machine Learning", "Docker", "Kubernetes", "PostgreSQL"],
            "experience_min": 5,
            "experience_max": 10,
            "source": "demo",
            "source_url": "https://example.com/jobs/ai-ml-engineer",
            "salary_currency": "INR",
        },
        {
            "title": "Frontend Lead (React + TypeScript)",
            "company": "DesignStack",
            "location": "Delhi, India",
            "remote": True,
            "salary_min": 2200000,
            "salary_max": 3800000,
            "currency": "INR",
            "description": "Lead frontend architecture for our design collaboration platform. Drive component library development and frontend best practices.",
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
            "description": "Design and maintain cloud infrastructure for our SaaS platform. Automate everything from deployments to incident response.",
            "required_skills": ["Docker", "Python", "PostgreSQL", "Redis"],
            "experience_min": 3,
            "experience_max": 7,
            "source": "demo",
            "source_url": "https://example.com/jobs/devops-engineer",
        },
    ]

    for job in jobs:
        job_id = str(uuid4())
        skills = job.pop("required_skills")
        await session.execute(
            text("""
                INSERT INTO career.jobs (id, title, company, location, remote, salary_min, salary_max,
                    salary_currency, description, required_skills, experience_min, experience_max,
                    source, source_url, posted_at, expiry_date)
                VALUES (:id, :title, :company, :location, :remote, :salary_min, :salary_max,
                    :salary_currency, :description, :required_skills, :experience_min, :experience_max,
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
                "salary_currency": job.get("salary_currency", "INR"),
                "description": job["description"],
                "required_skills": skills,
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
