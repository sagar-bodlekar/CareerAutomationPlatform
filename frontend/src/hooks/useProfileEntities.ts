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
  addSocialLink,
  updateSocialLink,
  deleteSocialLink,
  addCertification,
  updateCertification,
  deleteCertification,
  addLanguage,
  updateLanguage,
  deleteLanguage,
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

// ─── Social Link Hooks ───────────────────────────────────────

export function useAddSocialLink() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Record<string, unknown> }) =>
      addSocialLink(profileId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateSocialLink() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ linkId, data }: { linkId: string; data: Record<string, unknown> }) =>
      updateSocialLink(linkId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useDeleteSocialLink() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (linkId: string) => deleteSocialLink(linkId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

// ─── Certification Hooks ─────────────────────────────────────

export function useAddCertification() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Record<string, unknown> }) =>
      addCertification(profileId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateCertification() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ certId, data }: { certId: string; data: Record<string, unknown> }) =>
      updateCertification(certId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useDeleteCertification() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (certId: string) => deleteCertification(certId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

// ─── Language Hooks ───────────────────────────────────────────

export function useAddLanguage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ profileId, data }: { profileId: string; data: Record<string, unknown> }) =>
      addLanguage(profileId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useUpdateLanguage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ langId, data }: { langId: string; data: Record<string, unknown> }) =>
      updateLanguage(langId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

export function useDeleteLanguage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (langId: string) => deleteLanguage(langId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}
