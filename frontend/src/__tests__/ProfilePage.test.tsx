import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "../context/AuthContext";
import { ToastProvider } from "../context/ToastContext";
import ProfilePage from "../pages/ProfilePage";

function renderPage() {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });

  localStorage.setItem("access_token", "mock-token");
  localStorage.setItem(
    "user",
    JSON.stringify({ id: "user-001", email: "jane.doe@example.com", role: "user" }),
  );

  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/profile"]}>
        <AuthProvider>
          <ToastProvider>
            <ProfilePage />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ProfilePage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders profile page title", async () => {
    renderPage();
    expect(screen.getByText("Profile")).toBeInTheDocument();
  });

  it("loads and displays user profile data from API", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Jane Doe")).toBeInTheDocument();
    });

    // Should show skills section
    expect(screen.getByText("Skills")).toBeInTheDocument();
    expect(screen.getByText("Experience")).toBeInTheDocument();
    expect(screen.getByText("Education")).toBeInTheDocument();
  });

  it("has edit button linking to profile edit page", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("Edit Profile")).toBeInTheDocument();
    });

    expect(screen.getByText("Edit Profile").closest("a")).toHaveAttribute("href", "/profile/edit");
  });
});
