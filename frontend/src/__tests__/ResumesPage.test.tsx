import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { ToastProvider } from "../context/ToastContext";
import ResumesPage from "../pages/ResumesPage";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { describe, it, expect, beforeEach } from "vitest";

const BASE = "/api/v1";

function renderPage() {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });

  localStorage.setItem("access_token", "mock-token");
  localStorage.setItem(
    "user",
    JSON.stringify({ id: "user-001", email: "test@example.com", role: "user" }),
  );

  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/resumes"]}>
        <AuthProvider>
          <ToastProvider>
            <ResumesPage />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ResumesPage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders the page title", async () => {
    renderPage();
    expect(screen.getByText("Resumes")).toBeInTheDocument();
  });

  it("shows the Generate Resume button", async () => {
    renderPage();
    // The button is always visible in the header, regardless of data state
    const buttons = screen.getAllByText(/Generate Resume/i);
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it("renders resume cards when data loads", async () => {
    renderPage();

    // Should show resume titles from mock data
    await waitFor(() => {
      expect(screen.getByText(/Master Resume/i)).toBeInTheDocument();
    });
  });

  it("renders error state when API fails", async () => {
    server.use(
      http.get(`${BASE}/resumes`, async () => {
        return HttpResponse.json(
          { success: false, data: null, errors: [{ code: "SERVER_ERROR", message: "Failed to load resumes" }] },
          { status: 500 },
        );
      }),
    );

    renderPage();

    await waitFor(
      () => {
        expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
      },
      { timeout: 10000 },
    );
  });

  it("renders empty state when no resumes exist", async () => {
    server.use(
      http.get(`${BASE}/resumes`, async () => {
        return HttpResponse.json({
          success: true,
          data: [],
          meta: { page: 1, per_page: 20, total: 0, total_pages: 0 },
          errors: null,
        });
      }),
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/No resumes yet/i)).toBeInTheDocument();
    });

    // Should show CTA to generate first resume
    const ctaLinks = screen.getAllByText(/Generate Your First Resume/i);
    expect(ctaLinks.length).toBeGreaterThanOrEqual(1);
  });
});
