import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getApplications, getApplication, createApplication, submitApplication } from "../services/applications";

export function useApplications(profileId: string, status?: string) {
  return useQuery({
    queryKey: ["applications", profileId, status],
    queryFn: () => getApplications(profileId, status),
    enabled: !!profileId,
    staleTime: 30_000,        // 30s — near-real-time
    refetchInterval: 60_000,  // Poll every 60s for status changes
  });
}

export function useApplication(id: number) {
  return useQuery({
    queryKey: ["application", id],
    queryFn: () => getApplication(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}

export function useCreateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { profile_id: string; job_id: number; company_name?: string; job_title?: string; match_score?: number }) =>
      createApplication(data as Parameters<typeof createApplication>[0]),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
      qc.invalidateQueries({ queryKey: ["tracking", "funnel"] });
    },
  });
}

export function useSubmitApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => submitApplication(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      qc.invalidateQueries({ queryKey: ["application"] });
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
      qc.invalidateQueries({ queryKey: ["tracking", "funnel"] });
    },
  });
}
