import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getResumes, getResume, createResume, generateResume } from "../services/resumes";

export function useResumes(profileId: string) {
  return useQuery({
    queryKey: ["resumes", profileId],
    queryFn: () => getResumes(profileId),
    enabled: !!profileId,
    staleTime: 2 * 60 * 1000, // 2 min
  });
}

export function useResume(id: string) {
  return useQuery({
    queryKey: ["resume", id],
    queryFn: () => getResume(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateResume() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, title }: { profileId: string; title: string }) => createResume(profileId, title),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
}

export function useGenerateResume() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, targetRole, jobId }: { id: string; targetRole: string; jobId?: number }) =>
      generateResume(id, targetRole, jobId),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["resumes"] });
      qc.invalidateQueries({ queryKey: ["resume", variables.id] });
    },
  });
}
