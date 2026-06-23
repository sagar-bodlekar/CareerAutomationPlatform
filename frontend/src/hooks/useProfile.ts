import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProfile, createProfile, updateProfile } from "../services/profiles";
import type { Profile } from "../types";

export function useProfile(id: string) {
  return useQuery({
    queryKey: ["profile", id],
    queryFn: () => getProfile(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 min — rarely changes
  });
}

export function useCreateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: Partial<Profile> }) =>
      createProfile(userId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
    },
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Partial<Profile> }) =>
      updateProfile(profileId, data),
    onMutate: async () => {
      // Cancel outgoing refetches so they don't overwrite optimistic update
      await qc.cancelQueries({ queryKey: ["profile"] });

      // Snapshot previous profile for rollback
      const previous = qc.getQueriesData<Profile>({ queryKey: ["profile"] });

      return { previous };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
    },
    onError: (_err, _vars, context) => {
      // Rollback to snapshot on error
      if (context?.previous) {
        for (const [key, data] of context.previous) {
          qc.setQueryData(key, data);
        }
      }
    },
  });
}
