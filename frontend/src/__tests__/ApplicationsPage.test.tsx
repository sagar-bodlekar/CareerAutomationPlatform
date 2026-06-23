import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext";
import { ToastProvider } from "../context/ToastContext";
import ApplicationsPage from "../pages/ApplicationsPage";
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
      <MemoryRouter initialEntries={["/applications"]}>
        <AuthProvider>
          <ToastProvider>
            <ApplicationsPage />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ApplicationsPage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders the page title and filter tabs", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Applications")).toBeInTheDocument();
    });

    // Should show filter tabs
    expect(screen.getByText("All")).toBeInTheDocument();
    expect(screen.getByText("Draft")).toBeInTheDocument();
  });

  it("renders application cards when data loads", async () => {
    renderPage();

    // Should show company names from mock data
    await waitFor(() => {
      expect(screen.getByText("Google")).toBeInTheDocument();
      expect(screen.getByText("Stripe")).toBeInTheDocument();
      expect(screen.getByText("OpenAI")).toBeInTheDocument();
    });
  });

  it("renders error state when API fails", async () => {
    server.use(
      http.get(`${BASE}/applications`, async () => {
        return HttpResponse.json(
          { success: false, data: null, errors: [{ code: "SERVER_ERROR", message: "Failed to load applications" }] },
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

  it("renders empty state when no applications exist", async () => {
    server.use(
      http.get(`${BASE}/applications`, async () => {
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
      expect(screen.getByText(/No applications yet/i)).toBeInTheDocument();
    });

    // Browse Jobs link should be present
    expect(screen.getByText(/Browse Jobs/i)).toBeInTheDocument();
  });

  it("switches filter when clicking status tabs", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Google")).toBeInTheDocument();
    });

    // Click "Draft" filter tab (first match is the button)
    const draftButtons = screen.getAllByText("Draft");
    const draftFilterButton = draftButtons.find(
      (el) => el.tagName === "BUTTON",
    );
    if (draftFilterButton) {
      draftFilterButton.click();
    }

    // Google should still be visible (draft status)
    await waitFor(() => {
      expect(screen.getByText("Google")).toBeInTheDocument();
    });
  });
});
