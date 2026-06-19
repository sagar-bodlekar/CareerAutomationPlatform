import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  addExperience,
  updateExperience,
  deleteExperience,
  addEducation,
  updateEducation,
  deleteEducation,
  addProject,
  updateProject,
  deleteProject,
  deleteSkill,
  bulkAddSkills,
} from "../services/profiles";

// ─── Experience Hooks ─────────────────────────────────────────

export function useAddExperience() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Record<string, unknown> }) =>
      addExperience(profileId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateExperience() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ expId, data }: { expId: string; data: Record<string, unknown> }) =>
      updateExperience(expId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useDeleteExperience() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (expId: string) => deleteExperience(expId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

// ─── Education Hooks ──────────────────────────────────────────

export function useAddEducation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Record<string, unknown> }) =>
      addEducation(profileId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateEducation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ eduId, data }: { eduId: string; data: Record<string, unknown> }) =>
      updateEducation(eduId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useDeleteEducation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (eduId: string) => deleteEducation(eduId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

// ─── Project Hooks ────────────────────────────────────────────

export function useAddProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Record<string, unknown> }) =>
      addProject(profileId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ projId, data }: { projId: string; data: Record<string, unknown> }) =>
      updateProject(projId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (projId: string) => deleteProject(projId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

// ─── Skill Hooks ──────────────────────────────────────────────

export function useDeleteSkill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (skillId: string) => deleteSkill(skillId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useBulkAddSkills() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, skills }: { profileId: string; skills: Array<{ name: string; category?: string; proficiency?: string }> }) =>
      bulkAddSkills(profileId, skills),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}
