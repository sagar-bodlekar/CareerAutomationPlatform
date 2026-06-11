import { createItem, updateItem, getById } from "./api";
import type { Profile } from "../types";

export async function getProfile(id: number): Promise<Profile> {
  return getById(`/profiles/${id}`);
}

export async function createProfile(data: Partial<Profile>): Promise<Profile> {
  return createItem("/profiles", data);
}

export async function updateProfile(id: number, data: Partial<Profile>): Promise<Profile> {
  return updateItem(`/profiles/${id}`, data);
}

export async function exportProfile(id: number): Promise<Profile> {
  return getById(`/profiles/${id}/export`);
}

export async function importProfile(id: number, data: Profile): Promise<Profile> {
  return createItem(`/profiles/${id}/import`, data);
}

export async function getProfileAnalytics(id: number) {
  return getById(`/profiles/${id}/analytics`);
}
