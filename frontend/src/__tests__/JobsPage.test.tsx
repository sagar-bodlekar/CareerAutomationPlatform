import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { ToastProvider } from "../context/ToastContext";
import JobsPage from "../pages/JobsPage";
import { http, HttpResponse } from "msw";
import { server } from "../mocks/server";
import { describe, it, expect, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";

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
      <MemoryRouter initialEntries={["/jobs"]}>
        <AuthProvider>
          <ToastProvider>
            <JobsPage />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("JobsPage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders loading skeletons while fetching jobs", async () => {
    server.use(
      http.get(`${BASE}/jobs`, async () => {
        await new Promise((r) => setTimeout(r, 500));
        return HttpResponse.json({ success: true, data: [], errors: null });
      }),
    );

    renderPage();
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThanOrEqual(1);
  });

  it("renders job cards when data loads", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Jobs")).toBeInTheDocument();
    });

    // Should show job titles
    await waitFor(() => {
      expect(screen.getByText(/Senior Frontend Engineer/i)).toBeInTheDocument();
      expect(screen.getByText(/Full Stack Engineer/i)).toBeInTheDocument();
    });

    // Should show company names
    expect(screen.getByText("Google")).toBeInTheDocument();
    expect(screen.getByText("Stripe")).toBeInTheDocument();
  });

  it("renders error state with retry when API fails", async () => {
    server.use(
      http.get(`${BASE}/jobs`, async () => {
        return HttpResponse.json(
          { success: false, data: null, errors: [{ code: "SERVER_ERROR", message: "Failed to load jobs" }] },
          { status: 500 },
        );
      }),
    );

    renderPage();

    // Axios interceptor retries 2 times (1s + 2s) before error surfaces
    await waitFor(
      () => {
        expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
      },
      { timeout: 10000 },
    );

    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });

  it("renders empty state when no jobs found", async () => {
    server.use(
      http.get(`${BASE}/jobs`, async () => {
        return HttpResponse.json({
          success: true,
          data: [],
          meta: { page: 1, per_page: 10, total: 0, total_pages: 0 },
          errors: null,
        });
      }),
    );

    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/No jobs found/i)).toBeInTheDocument();
    });
  });

  it("shows filter panel when Filters button is clicked", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText(/Senior Frontend Engineer/i)).toBeInTheDocument();
    });

    // Click the Filters button
    const filtersButton = screen.getByText(/Filters/i);
    await userEvent.click(filtersButton);

    // Filter panel should now be visible
    expect(screen.getByText(/Location Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Employment Type/i)).toBeInTheDocument();
    expect(screen.getByText(/Min Salary/i)).toBeInTheDocument();
    expect(screen.getByText(/Max Salary/i)).toBeInTheDocument();
  });
});
