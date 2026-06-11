import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProfile, createProfile, updateProfile } from "../services/profiles";
import type { Profile } from "../types";

export function useProfile(id: number) {
  return useQuery({
    queryKey: ["profile", id],
    queryFn: () => getProfile(id),
    enabled: !!id,
  });
}

export function useCreateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Profile>) => createProfile(data),
    onSuccess: (profile) => {
      qc.invalidateQueries({ queryKey: ["profile", profile.id] });
    },
  });
}

export function useUpdateProfile(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Profile>) => updateProfile(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile", id] });
    },
  });
}
