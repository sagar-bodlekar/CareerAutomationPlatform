import { http, HttpResponse, delay } from "msw";
import {
  mockProfile,
  mockJobs,
  mockApplications,
  mockResumes,
  mockTemplates,
  mockNotifications,
  mockMatch,
  mockStats,
  mockAnalytics,
  mockFunnel,
  mockDailyTrends,
} from "./data";

const BASE = "/api/v1";

let nextAppId = 100;
let nextResumeId = 100;

export const handlers = [
  // ── Auth ─────────────────────────────────────────────
  http.get(`${BASE}/auth/me`, async () => {
    await delay(100);
    return HttpResponse.json({
      success: true,
      data: { id: "user-001", email: "jane.doe@example.com", role: "user" },
      errors: null,
    });
  }),

  http.post(`${BASE}/auth/login`, async () => {
    await delay(300);
    return HttpResponse.json({
      success: true,
      data: {
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        user: { id: "user-001", email: "jane.doe@example.com", role: "user" },
      },
      errors: null,
    });
  }),

  http.post(`${BASE}/auth/register`, async () => {
    await delay(300);
    return HttpResponse.json({
      success: true,
      data: {
        access_token: "mock-access-token",
        refresh_token: "mock-refresh-token",
        user: { id: "user-001", email: "jane.doe@example.com", role: "user" },
      },
      errors: null,
    });
  }),

  http.post(`${BASE}/auth/refresh`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: {
        access_token: "mock-refreshed-access-token",
        refresh_token: "mock-refreshed-refresh-token",
      },
      errors: null,
    });
  }),

  // ── Profile ──────────────────────────────────────────
  http.get(`${BASE}/profiles/user/:userId`, async ({ params }) => {
    await delay(200);
    if (params.userId === "not-found") {
      return HttpResponse.json(
        { success: false, data: null, errors: [{ code: "NOT_FOUND", message: "Profile not found" }] },
        { status: 404 },
      );
    }
    return HttpResponse.json({
      success: true,
      data: mockProfile,
      errors: null,
    });
  }),

  http.put(`${BASE}/profiles/:profileId`, async ({ request }) => {
    await delay(400);
    const body = await request.json();
    return HttpResponse.json({
      success: true,
      data: { ...mockProfile, ...(body as object), updated_at: new Date().toISOString() },
      errors: null,
    });
  }),

  http.post(`${BASE}/profiles`, async ({ request }) => {
    await delay(400);
    const body = await request.json();
    return HttpResponse.json({
      success: true,
      data: { ...mockProfile, ...(body as object), id: "prof-new", created_at: new Date().toISOString() },
      errors: null,
    });
  }),

  // ── Profile entities (experience, education, projects, etc.) ──
  http.post(`${BASE}/profiles/:id/experiences`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "exp-new" }, errors: null });
  }),
  http.put(`${BASE}/experiences/:id`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "exp-updated" }, errors: null });
  }),
  http.delete(`${BASE}/experiences/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  http.post(`${BASE}/profiles/:id/education`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "edu-new" }, errors: null });
  }),
  http.put(`${BASE}/education/:id`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "edu-updated" }, errors: null });
  }),
  http.delete(`${BASE}/education/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  http.post(`${BASE}/profiles/:id/projects`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "proj-new" }, errors: null });
  }),
  http.put(`${BASE}/projects/:id`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "proj-updated" }, errors: null });
  }),
  http.delete(`${BASE}/projects/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  http.post(`${BASE}/profiles/:id/certifications`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "cert-new" }, errors: null });
  }),
  http.put(`${BASE}/certifications/:id`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "cert-updated" }, errors: null });
  }),
  http.delete(`${BASE}/certifications/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  http.post(`${BASE}/profiles/:id/languages`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "lang-new" }, errors: null });
  }),
  http.put(`${BASE}/languages/:id`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "lang-updated" }, errors: null });
  }),
  http.delete(`${BASE}/languages/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  http.post(`${BASE}/profiles/:id/social-links`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "link-new" }, errors: null });
  }),
  http.put(`${BASE}/social-links/:id`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { id: "link-updated" }, errors: null });
  }),
  http.delete(`${BASE}/social-links/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  http.post(`${BASE}/profiles/:id/skills/bulk`, async () => {
    await delay(300);
    return HttpResponse.json({ success: true, data: { count: 5 }, errors: null });
  }),
  http.delete(`${BASE}/skills/:id`, async () => {
    await delay(200);
    return HttpResponse.json({ success: true, data: null, errors: null });
  }),

  // ── Jobs ─────────────────────────────────────────────
  http.get(`${BASE}/jobs`, async ({ request }) => {
    await delay(300);
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get("page") ?? "1", 10);
    const perPage = parseInt(url.searchParams.get("per_page") ?? "10", 10);
    const query = url.searchParams.get("query")?.toLowerCase() ?? "";

    let filtered = mockJobs;
    if (query) {
      filtered = mockJobs.filter(
        (j) =>
          j.title.toLowerCase().includes(query) ||
          j.company_name.toLowerCase().includes(query) ||
          j.required_skills.some((s) => s.toLowerCase().includes(query)),
      );
    }

    const start = (page - 1) * perPage;
    const paged = filtered.slice(start, start + perPage);

    return HttpResponse.json({
      success: true,
      data: paged,
      meta: {
        page,
        per_page: perPage,
        total: filtered.length,
        total_pages: Math.ceil(filtered.length / perPage),
      },
      errors: null,
    });
  }),

  http.get(`${BASE}/jobs/:id`, async ({ params }) => {
    await delay(200);
    const job = mockJobs.find((j) => j.id === Number(params.id));
    if (!job) {
      return HttpResponse.json(
        { success: false, data: null, errors: [{ code: "NOT_FOUND", message: "Job not found" }] },
        { status: 404 },
      );
    }
    return HttpResponse.json({
      success: true,
      data: job,
      errors: null,
    });
  }),

  // ── Matches ──────────────────────────────────────────
  http.get(`${BASE}/matches/score`, async () => {
    await delay(300);
    return HttpResponse.json({
      success: true,
      data: mockMatch,
      errors: null,
    });
  }),

  http.get(`${BASE}/matches/recommendations/:profileId`, async () => {
    await delay(300);
    return HttpResponse.json({
      success: true,
      data: [
        { ...mockJobs[0], match_score: 92 },
        { ...mockJobs[1], match_score: 85 },
        { ...mockJobs[2], match_score: 78 },
      ],
      errors: null,
    });
  }),

  // ── Applications ─────────────────────────────────────
  http.get(`${BASE}/applications`, async ({ request }) => {
    await delay(200);
    const url = new URL(request.url);
    const status = url.searchParams.get("status");
    let filtered = mockApplications;
    if (status) {
      filtered = mockApplications.filter((a) => a.status === status);
    }
    return HttpResponse.json({
      success: true,
      data: filtered,
      meta: { page: 1, per_page: 20, total: filtered.length, total_pages: 1 },
      errors: null,
    });
  }),

  http.get(`${BASE}/applications/:id`, async ({ params }) => {
    await delay(200);
    const app = mockApplications.find((a) => a.id === Number(params.id));
    if (!app) {
      return HttpResponse.json(
        { success: false, data: null, errors: [{ code: "NOT_FOUND", message: "Application not found" }] },
        { status: 404 },
      );
    }
    return HttpResponse.json({
      success: true,
      data: app,
      errors: null,
    });
  }),

  http.post(`${BASE}/applications`, async () => {
    await delay(400);
    nextAppId += 1;
    const newApp = {
      ...mockApplications[0],
      id: nextAppId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json({
      success: true,
      data: newApp,
      errors: null,
    });
  }),

  http.post(`${BASE}/applications/:id/submit`, async () => {
    await delay(500);
    return HttpResponse.json({
      success: true,
      data: { status: "sent", sent_at: new Date().toISOString() },
      errors: null,
    });
  }),

  http.get(`${BASE}/applications/:id/events`, async ({ params }) => {
    await delay(200);
    const app = mockApplications.find((a) => a.id === Number(params.id));
    return HttpResponse.json({
      success: true,
      data: app?.events ?? [],
      errors: null,
    });
  }),

  // ── Resumes ──────────────────────────────────────────
  http.get(`${BASE}/resumes`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockResumes,
      meta: { page: 1, per_page: 20, total: mockResumes.length, total_pages: 1 },
      errors: null,
    });
  }),

  http.get(`${BASE}/resumes/:id`, async ({ params }) => {
    await delay(200);
    const resume = mockResumes.find((r) => r.id === params.id);
    if (!resume) {
      return HttpResponse.json(
        { success: false, data: null, errors: [{ code: "NOT_FOUND", message: "Resume not found" }] },
        { status: 404 },
      );
    }
    return HttpResponse.json({
      success: true,
      data: resume,
      errors: null,
    });
  }),

  http.post(`${BASE}/resumes`, async () => {
    await delay(300);
    nextResumeId += 1;
    return HttpResponse.json({
      success: true,
      data: { ...mockResumes[0], id: `res-${nextResumeId}`, created_at: new Date().toISOString() },
      errors: null,
    });
  }),

  http.post(`${BASE}/resumes/:id/generate`, async () => {
    await delay(1000);
    return HttpResponse.json({
      success: true,
      data: { ...mockResumes[0], ats_score: 90, version: 3 },
      errors: null,
    });
  }),

  http.post(`${BASE}/resumes/:id/optimize`, async () => {
    await delay(800);
    return HttpResponse.json({
      success: true,
      data: { ats_score: 92, before_score: 85, improvements: ["Added 5 missing keywords", "Optimized section headers"] },
      errors: null,
    });
  }),

  http.get(`${BASE}/resumes/:id/download`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: { url: "https://example.com/resume.pdf" },
      errors: null,
    });
  }),

  http.get(`${BASE}/resumes/templates`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockTemplates,
      errors: null,
    });
  }),

  // ── Outreach ─────────────────────────────────────────
  http.post(`${BASE}/outreach/cover-letter`, async () => {
    await delay(600);
    return HttpResponse.json({
      success: true,
      data: {
        id: "cl-001",
        content_type: "cover_letter",
        body: "Dear Hiring Manager,\n\nI am writing to express my strong interest in the Senior Frontend Engineer position at Google. With over 6 years of experience building scalable web applications...",
        tone: "professional",
        status: "generated",
        version: 1,
        created_at: new Date().toISOString(),
      },
      errors: null,
    });
  }),

  http.post(`${BASE}/outreach/email`, async () => {
    await delay(500);
    return HttpResponse.json({
      success: true,
      data: {
        id: "em-001",
        content_type: "email",
        subject: "Application for Senior Frontend Engineer Position",
        body: "Dear Hiring Team,\n\nI am excited to apply for the Senior Frontend Engineer role at Google...",
        tone: "professional",
        status: "generated",
        version: 1,
        created_at: new Date().toISOString(),
      },
      errors: null,
    });
  }),

  // ── Tracking ─────────────────────────────────────────
  http.get(`${BASE}/tracking/stats`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockStats,
      errors: null,
    });
  }),

  http.get(`${BASE}/tracking/analytics`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockAnalytics,
      errors: null,
    });
  }),

  http.get(`${BASE}/tracking/funnel`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockFunnel,
      errors: null,
    });
  }),

  http.get(`${BASE}/tracking/trends`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockDailyTrends,
      errors: null,
    });
  }),

  http.post(`${BASE}/tracking/export`, async () => {
    await delay(300);
    return HttpResponse.json({
      success: true,
      data: { content: "id,status,company,job_title\n1,draft,Google,Senior Frontend Engineer", filename: "tracking-export.csv" },
      errors: null,
    });
  }),

  http.get(`${BASE}/tracking/activity`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: [
        { id: 1, type: "application", description: "Applied to Senior Frontend Engineer at Google", timestamp: new Date(Date.now() - 3600000).toISOString() },
        { id: 2, type: "match", description: "New match: Full Stack Engineer at Stripe (85%)", timestamp: new Date(Date.now() - 7200000).toISOString() },
        { id: 3, type: "reply", description: "OpenAI replied to your application", timestamp: new Date(Date.now() - 86400000).toISOString() },
      ],
      errors: null,
    });
  }),

  http.get(`${BASE}/tracking/applications`, async () => {
    await delay(100);
    return HttpResponse.json({
      success: true,
      data: [],
      meta: { page: 1, per_page: 20, total: 0, total_pages: 0 },
      errors: null,
    });
  }),

  // ── Notifications ────────────────────────────────────
  http.get(`${BASE}/notifications`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: mockNotifications,
      errors: null,
    });
  }),

  http.get(`${BASE}/notifications/unread`, async () => {
    await delay(100);
    return HttpResponse.json({
      success: true,
      data: mockNotifications.filter((n) => !n.read).length,
      errors: null,
    });
  }),

  http.put(`${BASE}/notifications/:id/read`, async () => {
    await delay(200);
    return HttpResponse.json({
      success: true,
      data: { success: true },
      errors: null,
    });
  }),

  http.put(`${BASE}/notifications/read-all`, async () => {
    await delay(300);
    return HttpResponse.json({
      success: true,
      data: { success: true },
      errors: null,
    });
  }),

  // ── Error simulation endpoint (for testing error states) ──
  http.get(`${BASE}/error-test`, async () => {
    await delay(100);
    return HttpResponse.json(
      { success: false, data: null, errors: [{ code: "SERVER_ERROR", message: "Internal server error" }] },
      { status: 500 },
    );
  }),
];
