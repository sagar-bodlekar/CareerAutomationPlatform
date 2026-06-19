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
    onSuccess: () => {
      // Invalidate all profile queries (cache key uses auth user ID, not profile ID)
      qc.invalidateQueries({ queryKey: ["profile"] });
      // Profile changes affect tracking stats
      qc.invalidateQueries({ queryKey: ["tracking", "stats"] });
    },
  });
}
