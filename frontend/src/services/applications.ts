import { createItem, updateItem, getById, getList, postAction } from "./api";
import type { Application } from "../types";

export async function getApplications(profileId: string, status?: string, page = 1, perPage = 20) {
  return getList<Application>("/applications", { profile_id: profileId, status, page, per_page: perPage });
}

export async function getApplication(id: number): Promise<Application> {
  return getById(`/applications/${id}`);
}

export async function createApplication(data: {
  profile_id: string;
  job_id: number;
  company_name?: string;
  job_title?: string;
  job_location?: string;
  match_score?: number;
}): Promise<Application> {
  return createItem("/applications", data);
}

export async function updateApplication(id: number, data: Partial<Application>): Promise<Application> {
  return updateItem(`/applications/${id}/status`, data);
}

export async function submitApplication(id: number): Promise<Application> {
  return postAction(`/applications/${id}/submit`);
}

export async function getApplicationEvents(id: number) {
  const { default: api } = await import("./api");
  const { data } = await api.get(`/applications/${id}/events`);
  return data.data;
}
