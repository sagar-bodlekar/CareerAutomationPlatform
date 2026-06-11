import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import JobCard from "../components/jobs/JobCard";
import type { Job } from "../types";

const mockJob: Job = {
  id: 1,
  title: "Software Engineer",
  company_name: "Tech Corp",
  location: "San Francisco, CA",
  location_type: "remote",
  employment_type: "full-time",
  salary_min: 120000,
  salary_max: 180000,
  salary_currency: "USD",
  description: "Great job",
  required_skills: ["Python", "React"],
  preferred_skills: ["Go"],
  posted_date: "2026-06-10T00:00:00Z",
  source_url: "https://example.com/job/1",
};

describe("JobCard", () => {
  it("renders job details", () => {
    render(
      <BrowserRouter>
        <JobCard job={mockJob} matchScore={85} />
      </BrowserRouter>,
    );
    expect(screen.getByText("Software Engineer")).toBeInTheDocument();
    expect(screen.getByText("Tech Corp")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("React")).toBeInTheDocument();
  });

  it("links to job detail page", () => {
    render(
      <BrowserRouter>
        <JobCard job={mockJob} />
      </BrowserRouter>,
    );
    expect(screen.getByText("Software Engineer").closest("a")).toHaveAttribute("href", "/jobs/1");
  });
});
