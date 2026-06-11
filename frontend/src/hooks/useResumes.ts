import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getResumes, getResume, createResume, generateResume } from "../services/resumes";

export function useResumes(profileId: number) {
  return useQuery({
    queryKey: ["resumes", profileId],
    queryFn: () => getResumes(profileId),
    enabled: !!profileId,
  });
}

export function useResume(id: number) {
  return useQuery({
    queryKey: ["resume", id],
    queryFn: () => getResume(id),
    enabled: !!id,
  });
}

export function useCreateResume() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, title }: { profileId: number; title: string }) => createResume(profileId, title),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
}

export function useGenerateResume() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, targetRole, jobId }: { id: number; targetRole: string; jobId?: number }) =>
      generateResume(id, targetRole, jobId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
}
