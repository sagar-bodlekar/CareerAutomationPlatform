import { createItem, updateItem, getById, getList, postAction } from "./api";
import type { Resume, ResumeTemplate } from "../types";

export async function getResumes(profileId: string) {
  return getList<Resume>(`/resumes`, { profile_id: profileId });
}

export async function getResume(id: string): Promise<Resume> {
  return getById(`/resumes/${id}`);
}

export async function createResume(profileId: string, title: string): Promise<Resume> {
  return createItem("/resumes", { profile_id: profileId, title });
}

export async function updateResume(id: string, data: Partial<Resume>): Promise<Resume> {
  return updateItem(`/resumes/${id}`, data);
}

export async function generateResume(id: string, targetRole: string, jobId?: number) {
  return postAction(`/resumes/${id}/generate`, { target_role: targetRole, job_id: jobId });
}

export async function optimizeResume(id: string) {
  return postAction(`/resumes/${id}/optimize`);
}

export async function getResumeDownloadUrl(id: string): Promise<string> {
  const { data } = await (await import("./api")).default.get(`/resumes/${id}/download`);
  return data.data.url;
}

export async function getTemplates() {
  return getList<ResumeTemplate>("/resumes/templates");
}
