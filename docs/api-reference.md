# API Reference — AI Career Automation Platform

> **Base URL:** `http://localhost/api/v1/`  
> **Content-Type:** `application/json`

## Authentication

Most endpoints require a JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Auth Endpoints

#### POST /auth/register
Create a new user account.

```bash
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securePass123", "name": "John Doe"}'
```
**Response:** `201` — User created with tokens.

#### POST /auth/login
Authenticate and receive JWT tokens.

```bash
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securePass123"}'
```
**Response:** `200` — Access + refresh tokens.

#### POST /auth/refresh
Refresh an expired access token.

```bash
curl -X POST http://localhost/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

#### POST /auth/logout
Invalidate refresh token.

#### POST /auth/change-password
Change password (requires current password).

---

## Profile Service

Base path: `/api/v1/profiles/`

### POST /profiles
Create a new user profile.

```bash
curl -X POST http://localhost/api/v1/profiles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "full_name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "location": "San Francisco, CA"
    },
    "skills": [
      {"name": "Python", "proficiency": "expert"},
      {"name": "React", "proficiency": "advanced"}
    ],
    "experiences": [
      {
        "company": "Tech Corp",
        "role": "Senior Engineer",
        "start_date": "2020-01-01",
        "end_date": null,
        "description": "Led platform team"
      }
    ]
  }'
```
**Response:** `201` — Profile created.

### GET /profiles/{id}
Get full profile with all nested data.

### PUT /profiles/{id}
Update profile fields (partial update).

### GET /profiles/{id}/export
Export full profile as JSON.

### POST /profiles/{id}/import
Import JSON profile data (merge or overwrite).

---

## Resume Service

Base path: `/api/v1/resumes/`

### POST /resumes
Create master resume from profile.

```bash
curl -X POST http://localhost/api/v1/resumes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": 1, "title": "Master Resume", "template": "modern"}'
```

### POST /resumes/{id}/generate
Generate role-specific resume PDF.

```bash
curl -X POST http://localhost/api/v1/resumes/1/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"target_role": "Senior Software Engineer", "job_id": 123, "optimize_ats": true}'
```

### GET /resumes/{id}/download
Download resume PDF (redirects to MinIO presigned URL).

### POST /resumes/{id}/optimize
Run ATS optimization. Returns score and recommendations.

---

## Job Service

Base path: `/api/v1/jobs/`

### GET /jobs
Search and filter jobs.

```bash
curl "http://localhost/api/v1/jobs?skills=Python,React&location=Remote&page=1&per_page=20"
```
**Query Parameters:**
- `q` — Full-text search
- `skills` — Comma-separated skill filter
- `location` — Location filter
- `remote` — Boolean (true/false)
- `min_salary`, `max_salary` — Salary range
- `page`, `per_page` — Pagination

### GET /jobs/{id}
Get job details with full description and requirements.

### POST /jobs/refresh
Trigger immediate job scraping.

---

## Match Service

Base path: `/api/v1/matches/`

### POST /matches/score
Score a profile against a job.

```bash
curl -X POST http://localhost/api/v1/matches/score \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": 1, "job_id": 123}'
```
**Response:** `{"match_score": 85, "skill_match": 90, "experience_match": 80, ...}`

### GET /matches/recommendations/{profileId}
Get top-N job recommendations for a profile.

### GET /matches/gaps/{profileId}/{jobId}
Get skill gap analysis for a profile-job pair.

---

## Outreach Service

Base path: `/api/v1/outreach/`

### POST /outreach/cover-letter
Generate a personalized cover letter.

```bash
curl -X POST http://localhost/api/v1/outreach/cover-letter \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": 1, "job_id": 123, "tone": "professional"}'
```

### POST /outreach/email
Generate outreach email content.

### GET /outreach/templates
List available cover letter and email templates.

---

## Application Service

Base path: `/api/v1/applications/`

### POST /applications
Create an application draft.

```bash
curl -X POST http://localhost/api/v1/applications \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": 1, "job_id": 123, "company_name": "Tech Corp", "job_title": "Software Engineer"}'
```

### GET /applications/{id}
Get application with timeline and state info.

### POST /applications/{id}/submit
Submit application (transitions to sent, triggers delivery).

### PATCH /applications/{id}/status
Manually update application status (with state machine validation).

### POST /applications/{id}/retry
Retry failed delivery.

### GET /applications
List applications with filters and pagination.

```bash
curl "http://localhost/api/v1/applications?profile_id=1&status=sent&page=1&per_page=20"
```

---

## Tracking Service

Base path: `/api/v1/tracking/`

### GET /tracking/stats
Get aggregate tracking statistics.

```
?profile_id=1
```
**Response:** `{"total_applications": 28, "total_sent": 24, ...}`

### GET /tracking/analytics
Get detailed analytics (funnel, daily trends, source breakdown).

### GET /tracking/funnel
Get application funnel data (status distribution).

### GET /tracking/trends
Get daily application trends (default 30 days).

### POST /tracking/export
Export application data as CSV or JSON.

```
?profile_id=1&format=csv
```

---

## Notification Service

Base path: `/api/v1/notifications/`

### GET /notifications
Get user notifications.

```
?user_id=1&limit=20&unread_only=false
```

### GET /notifications/unread/count
Get unread notification count.

### POST /notifications/{id}/read
Mark notification as read.

### POST /notifications/read-all
Mark all notifications as read.

### WebSocket /ws/notifications/{user_id}
Real-time notification stream.

```javascript
const ws = new WebSocket("ws://localhost/ws/notifications/1");
ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log("New notification:", notification);
};
```

---

## AI Orchestrator

Base path: `/api/v1/ai/`

### POST /ai/execute
Execute an AI task by agent name.

```bash
curl -X POST http://localhost/api/v1/ai/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agent": "resume_optimizer", "params": {"resume_id": 1, "job_id": 123}}'
```

### GET /ai/agents
List configured AI agents and their capabilities.

---

## Webhooks

Base path: `/api/v1/webhooks/`

### POST /webhooks/delivery
Generic email delivery webhook.

```bash
curl -X POST http://localhost/api/v1/webhooks/delivery \
  -H "Content-Type: application/json" \
  -d '{"message_id": "provider-msg-123", "status": "delivered", "provider": "smtp"}'
```

---

## Health & Metrics

### GET /health
Service health check. Available on all services.

**Response:** `{"status": "ok", "service": "service-name"}`

### GET /metrics
Prometheus metrics endpoint. Available on all services (Phase 10).

---

## Error Responses

All errors return consistent structure:

```json
{
  "detail": "Human-readable error message",
  "status_code": 400
}
```

Common status codes:
- `200` — Success
- `201` — Created
- `400` — Bad request (validation error)
- `401` — Unauthorized
- `403` — Forbidden
- `404` — Not found
- `409` — Conflict (duplicate)
- `422` — Unprocessable entity (validation)
- `429` — Too many requests (rate limited)
- `500` — Internal server error

## Rate Limiting

- **Auth endpoints:** 20 requests/minute with burst of 5
- **API endpoints:** 100 requests/minute with burst of 10
- **Webhooks:** No rate limiting
- **Response on limit:** `429 Too Many Requests` with `Retry-After` header
