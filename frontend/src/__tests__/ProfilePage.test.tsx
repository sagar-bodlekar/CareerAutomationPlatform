import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProfilePage from "../pages/ProfilePage";
import { AuthProvider } from "../context/AuthContext";

function renderWithProviders(ui: React.ReactElement) {
  const qc = new QueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <AuthProvider>{ui}</AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

describe("ProfilePage", () => {
  it("renders profile information", () => {
    renderWithProviders(<ProfilePage />);
    expect(screen.getByText("Profile")).toBeInTheDocument();
    expect(screen.getByText("Alex Johnson")).toBeInTheDocument();
    expect(screen.getByText("Senior Full Stack Engineer")).toBeInTheDocument();
    expect(screen.getByText("Skills")).toBeInTheDocument();
    expect(screen.getByText("Experience")).toBeInTheDocument();
    expect(screen.getByText("Education")).toBeInTheDocument();
  });

  it("has edit button", () => {
    renderWithProviders(<ProfilePage />);
    expect(screen.getByText("Edit Profile").closest("a")).toHaveAttribute("href", "/profile/edit");
  });
});
