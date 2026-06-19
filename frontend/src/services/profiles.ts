import { createItem, updateItem, getById, deleteItem } from "./api";
import type { Profile, WorkExperience, Education, Project, Skill } from "../types";

// Look up a profile by auth user ID (not profile ID)
// The backend has a dedicated endpoint for this
export async function getProfile(id: string): Promise<Profile> {
  return getById(`/profiles/user/${id}`);
}

export async function createProfile(userId: string, data: Partial<Profile>): Promise<Profile> {
  return createItem("/profiles", {
    user_id: userId,
    profile: data,
  });
}

export async function updateProfile(id: string, data: Partial<Profile>): Promise<Profile> {
  return updateItem(`/profiles/${id}`, data);
}

export async function exportProfile(id: string): Promise<Profile> {
  return getById(`/profiles/${id}/export`);
}

export async function importProfile(id: string, data: Profile): Promise<Profile> {
  return createItem(`/profiles/${id}/import`, data);
}

export async function getProfileAnalytics(id: string) {
  return getById(`/profiles/${id}/analytics`);
}

// ─── Work Experience ──────────────────────────────────────────

export async function addExperience(profileId: string, data: Record<string, unknown>): Promise<WorkExperience> {
  return createItem(`/profiles/${profileId}/experiences`, data);
}

export async function updateExperience(expId: string, data: Record<string, unknown>): Promise<WorkExperience> {
  return updateItem(`/experiences/${expId}`, data);
}

export async function deleteExperience(expId: string): Promise<void> {
  return deleteItem(`/experiences/${expId}`);
}

// ─── Education ────────────────────────────────────────────────

export async function addEducation(profileId: string, data: Record<string, unknown>): Promise<Education> {
  return createItem(`/profiles/${profileId}/education`, data);
}

export async function updateEducation(eduId: string, data: Record<string, unknown>): Promise<Education> {
  return updateItem(`/education/${eduId}`, data);
}

export async function deleteEducation(eduId: string): Promise<void> {
  return deleteItem(`/education/${eduId}`);
}

// ─── Projects ─────────────────────────────────────────────────

export async function addProject(profileId: string, data: Record<string, unknown>): Promise<Project> {
  return createItem(`/profiles/${profileId}/projects`, data);
}

export async function updateProject(projId: string, data: Record<string, unknown>): Promise<Project> {
  return updateItem(`/projects/${projId}`, data);
}

export async function deleteProject(projId: string): Promise<void> {
  return deleteItem(`/projects/${projId}`);
}

// ─── Skills (individual CRUD via dedicated endpoints) ─────────

export async function deleteSkill(skillId: string): Promise<void> {
  return deleteItem(`/skills/${skillId}`);
}

export async function bulkAddSkills(profileId: string, skills: Array<{ name: string; category?: string; proficiency?: string }>): Promise<Skill[]> {
  return createItem(`/profiles/${profileId}/skills/bulk`, { skills });
}
