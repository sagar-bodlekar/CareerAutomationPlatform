import { createItem, getById } from "./api";
import type { OutreachContent } from "../types";

export interface CoverLetterRequest {
  profile_id: string;
  job_id: number;
  company_name: string;
  job_title: string;
  candidate_name: string;
  current_role?: string;
  skills?: string[];
  achievements?: string[];
  tone?: string;
  use_ai?: boolean;
}

export interface EmailRequest {
  profile_id: string;
  job_id: number;
  company_name: string;
  job_title: string;
  candidate_name: string;
  current_role?: string;
  recipient_name?: string;
  recipient_role?: string;
  tone?: string;
  use_ai?: boolean;
}

export async function generateCoverLetter(request: CoverLetterRequest): Promise<OutreachContent> {
  return createItem("/outreach/cover-letter", request);
}

export async function generateEmail(request: EmailRequest): Promise<OutreachContent> {
  return createItem("/outreach/email", request);
}

export async function getCoverLetter(id: number): Promise<OutreachContent> {
  return getById(`/outreach/cover-letter/${id}`);
}

export async function getEmail(id: number): Promise<OutreachContent> {
  return getById(`/outreach/email/${id}`);
}

export async function getTemplates(contentType?: string) {
  const { default: api } = await import("./api");
  const params = contentType ? { content_type: contentType } : {};
  const { data } = await api.get("/outreach/templates", { params });
  return data.data;
}
