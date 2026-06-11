import { getById, postAction } from "./api";
import type { Match } from "../types";

export async function getRecommendations(profileId: number) {
  const { default: api } = await import("./api");
  const { data } = await api.get(`/matches/recommendations/${profileId}`);
  return data.data as Match[];
}

export async function scoreMatch(profileId: number, jobId: number): Promise<Match> {
  return postAction("/matches/score", { profile_id: profileId, job_id: jobId });
}

export async function getSkillGaps(profileId: number, jobId: number) {
  return getById(`/matches/gaps/${profileId}/${jobId}`);
}
