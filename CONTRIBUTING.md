# Contributing — AI Career Automation Platform

Thank you for considering contributing to the AI Career Automation Platform!

## Code of Conduct

This project follows a standard code of conduct. Be respectful, constructive, and professional in all interactions.

## How to Contribute

### 1. Reporting Bugs

- Check existing issues before creating a new one
- Use the bug report template
- Include steps to reproduce, expected behavior, and actual behavior
- Include environment details (OS, Python version, Docker version)

### 2. Suggesting Features

- Check existing issues and discussions
- Describe the feature and its use case
- Explain how it fits into the existing architecture

### 3. Code Contributions

#### Getting Started

```bash
# Fork and clone
git clone https://github.com/your-username/career-platform.git
cd career-platform

# Set up development environment
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -e backend/shared/
pip install -r backend/requirements-shared.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

#### Development Workflow

1. Create a branch: `git checkout -b feature/your-feature-name`
2. Make your changes following the code style
3. Write/update tests
4. Run tests locally: `make test`
5. Run linters: `make lint`
6. Commit with clear messages
7. Push and create a Pull Request

### Code Style

- **Python:** Follow [PEP 8](https://peps.python.org/pep-0008/)
- **TypeScript:** Follow project conventions (Prettier config)
- **Formatting:** Black (Python), Prettier (TypeScript)
- **Linting:** Ruff (Python), ESLint (TypeScript)
- **Type Checking:** mypy (Python), TypeScript strict mode

Key conventions:
- Use 4-space indentation for Python
- Use 2-space indentation for TypeScript/JSX
- Maximum line length: 100 characters (Python), 120 (TypeScript)
- Use descriptive variable names
- Add type hints for all Python functions
- Add JSDoc comments for TypeScript functions

### Testing

- All new features must include tests
- Maintain or improve code coverage
- Test both success and error paths
- Use pytest fixtures for test data

```bash
# Run tests
make test

# Run with coverage
pytest backend/ -v --cov=app --cov-report=html

# Run specific test
pytest backend/profile_service/tests/test_api.py -v -k "test_create_profile"
```

### Pull Request Process

1. **Title:** Clear and descriptive (e.g., "Add resume PDF generation")
2. **Description:** Explain what the PR does and why
3. **Testing:** Include test results
4. **Checklist:**
   - [ ] Tests pass (`make test`)
   - [ ] Linters pass (`make lint`)
   - [ ] Type checks pass (`cd frontend && npx tsc --noEmit`)
   - [ ] Documentation updated
   - [ ] Changelog entry added

### Architecture Guidelines

- **Microservices:** Each service is independent with its own Dockerfile and requirements
- **Shared library:** Common code goes in `backend/shared/`
- **Database:** All services share one PostgreSQL database (different schemas)
- **Events:** Use Celery for async tasks, Redis pub-sub for real-time events
- **Configuration:** Environment variables via `.env`, validated by Pydantic settings
- **API Design:** RESTful with consistent error responses

## Project Structure

```
career-platform/
├── backend/
│   ├── profile_service/       # User profile CRUD
│   ├── auth_service/          # Authentication & authorization
│   ├── resume_service/        # Resume generation & ATS optimization
│   ├── job_service/           # Job scraping & search
│   ├── match_service/         # Profile-job matching engine
│   ├── outreach_service/      # Cover letter & email generation
│   ├── application_service/   # Application pipeline & delivery
│   ├── tracking_service/      # Analytics & tracking
│   ├── ai_orchestrator/       # AI agent orchestration
│   ├── notification_service/  # User notifications
│   ├── shared/                # Shared libraries
│   └── service_template/      # Template for new services
├── frontend/                  # React dashboard
├── docs/                      # Documentation
├── docker/                    # Docker configs
│   ├── nginx/                 # API gateway config
│   ├── postgres/              # Database init scripts
│   ├── prometheus/            # Metrics config
│   ├── grafana/               # Dashboard configs
│   ├── loki/                  # Log aggregation config
│   ├── promtail/              # Log collector config
│   └── otel-collector/        # Tracing config
└── scripts/                   # Utility scripts
```

## Getting Help

- Check existing documentation in `docs/`
- Review the implementation plan: `docs/implementation-plan.md`
- Check architecture overview: `docs/architecture.md`
- Open a discussion for questions

## License

By contributing, you agree that your contributions will be licensed under the project's license.
