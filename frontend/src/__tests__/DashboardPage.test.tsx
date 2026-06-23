import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { ToastProvider } from "../context/ToastContext";
import DashboardPage from "../pages/DashboardPage";
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
      <MemoryRouter initialEntries={["/"]}>
        <AuthProvider>
          <ToastProvider>
            <DashboardPage />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("DashboardPage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders the welcome message and quick actions", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/Welcome/i)).toBeInTheDocument();
    });

    // Browse Jobs appears in both Quick Actions and Recent Activity sections
    const browseJobsLinks = screen.getAllByText("Browse Jobs");
    expect(browseJobsLinks.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Manage Resumes")).toBeInTheDocument();
    expect(screen.getByText("View Applications")).toBeInTheDocument();
    expect(screen.getByText("Edit Profile")).toBeInTheDocument();
  });

  it("renders stat card labels", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Active Applications")).toBeInTheDocument();
    });

    expect(screen.getByText("Applications Sent")).toBeInTheDocument();
    expect(screen.getByText("Delivered")).toBeInTheDocument();
    expect(screen.getByText("Replies")).toBeInTheDocument();
  });

  it("renders error state when tracking stats API fails", async () => {
    // DashboardPage checks statsError || activityError for the error state.
    // Override the tracking/stats endpoint to test the error fallback.
    server.use(
      http.get(`${BASE}/tracking/stats`, async () => {
        return HttpResponse.json(
          { success: false, data: null, errors: [{ code: "SERVER_ERROR", message: "Failed to load stats" }] },
          { status: 500 },
        );
      }),
    );

    renderPage();

    // Axios retries 2x (1s + 2s) before error surfaces
    await waitFor(
      () => {
        expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
      },
      { timeout: 12000 },
    );

    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  }, 20000);

  it("renders with zero stats available", async () => {
    server.use(
      http.get(`${BASE}/tracking/stats`, async () => {
        return HttpResponse.json({
          success: true,
          data: {
            total_applications: 0,
            total_sent: 0,
            total_delivered: 0,
            total_opened: 0,
            total_replied: 0,
            total_interviews: 0,
            total_offers: 0,
            success_rate: 0,
            avg_match_score: 0,
          },
          errors: null,
        });
      }),
    );

    renderPage();

    // Should render successfully with zero values (multiple 0 elements present)
    await waitFor(() => {
      const zeroElements = screen.getAllByText("0");
      expect(zeroElements.length).toBeGreaterThanOrEqual(1);
    });
  });
});
