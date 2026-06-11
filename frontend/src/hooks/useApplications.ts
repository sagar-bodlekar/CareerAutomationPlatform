import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getApplications, getApplication, createApplication, submitApplication } from "../services/applications";

export function useApplications(profileId: number, status?: string) {
  return useQuery({
    queryKey: ["applications", profileId, status],
    queryFn: () => getApplications(profileId, status),
    enabled: !!profileId,
  });
}

export function useApplication(id: number) {
  return useQuery({
    queryKey: ["application", id],
    queryFn: () => getApplication(id),
    enabled: !!id,
  });
}

export function useCreateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { profile_id: number; job_id: number; company_name?: string; job_title?: string }) =>
      createApplication(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}

export function useSubmitApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => submitApplication(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}
