import { getList, getById } from "./api";
import type { Job } from "../types";

export interface JobFilters {
  query?: string;
  skills?: string[];
  location?: string;
  location_type?: string;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
  page?: number;
  per_page?: number;
}

export async function searchJobs(filters: JobFilters = {}) {
  return getList<Job>("/jobs", filters as Record<string, unknown>);
}

export async function getJob(id: number): Promise<Job> {
  return getById(`/jobs/${id}`);
}

export async function refreshJobs() {
  const { default: api } = await import("./api");
  const { data } = await api.post("/jobs/refresh");
  return data.data;
}
