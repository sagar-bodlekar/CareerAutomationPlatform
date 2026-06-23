import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getApplications, getApplication, createApplication, submitApplication } from "../services/applications";
import type { Application } from "../types";

// ── Idempotency key helpers ──────────────────────────────
function getIdempotencyKey(prefix: string): string {
  const key = `${prefix}_${Date.now()}`;
  localStorage.setItem(`idempotency_${prefix}`, key);
  return key;
}

function isDuplicateSubmission(prefix: string): boolean {
  const stored = localStorage.getItem(`idempotency_${prefix}`);
  return stored !== null;
}

function clearIdempotencyKey(prefix: string): void {
  localStorage.removeItem(`idempotency_${prefix}`);
}

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
    mutationFn: (data: { profile_id: string; job_id: number; company_name?: string; job_title?: string; match_score?: number }) => {
      // Idempotency check — prevent double-submit for same job
      const dedupKey = `create_app_${data.profile_id}_${data.job_id}`;
      if (isDuplicateSubmission(dedupKey)) {
        clearIdempotencyKey(dedupKey);
      }
      getIdempotencyKey(dedupKey);
      return createApplication(data as Parameters<typeof createApplication>[0]);
    },
    onSuccess: (newApp) => {
      // Optimistic: immediately add to list caches
      const dedupKey = `create_app_${(newApp as any).profile_id}_${(newApp as any).job_id}`;
      clearIdempotencyKey(dedupKey);
      qc.setQueriesData<{ data: Application[]; meta: { total: number } }>(
        { queryKey: ["applications"] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            data: [newApp as unknown as Application, ...old.data],
            meta: { ...old.meta, total: old.meta.total + 1 },
          };
        },
      );
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
      qc.invalidateQueries({ queryKey: ["tracking", "funnel"] });
    },
    onError: (_err, _vars) => {
      // Rollback: invalidate to refetch from server
      qc.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}

export function useSubmitApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => {
      const dedupKey = `submit_app_${id}`;
      if (isDuplicateSubmission(dedupKey)) {
        throw new Error("Application submission already in progress");
      }
      getIdempotencyKey(dedupKey);
      return submitApplication(id);
    },
    onSuccess: (_data, id) => {
      const dedupKey = `submit_app_${id}`;
      clearIdempotencyKey(dedupKey);
      // Optimistic: immediately update the application status in cache
      qc.setQueriesData<{ data: Application[] }>(
        { queryKey: ["applications"] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            data: old.data.map((app) =>
              app.id === id ? { ...app, status: "sent" } : app,
            ),
          };
        },
      );
      qc.setQueryData<Application>(["application", id], (old) => {
        if (!old) return old;
        return { ...old, status: "sent" };
      });
      qc.invalidateQueries({ queryKey: ["applications"] });
      qc.invalidateQueries({ queryKey: ["application", id] });
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
      qc.invalidateQueries({ queryKey: ["tracking", "funnel"] });
    },
    onError: (_err, id) => {
      const dedupKey = `submit_app_${id}`;
      clearIdempotencyKey(dedupKey);
      // Rollback: invalidate to refetch from server
      qc.invalidateQueries({ queryKey: ["applications"] });
      qc.invalidateQueries({ queryKey: ["application", id] });
    },
  });
}
