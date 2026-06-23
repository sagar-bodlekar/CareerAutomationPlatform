import { useState, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  Briefcase,
  BookOpen,
  FolderGit2,
  Plus,
  X,
  Save,
  AlertCircle,
  ExternalLink,
  Award,
  Globe,
  BadgeCheck,
  Languages,
} from "lucide-react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useAuth } from "../context/AuthContext";
import { useProfile } from "../hooks/useProfile";
import {
  useAddExperience,
  useUpdateExperience,
  useDeleteExperience,
  useAddEducation,
  useUpdateEducation,
  useDeleteEducation,
  useAddProject,
  useUpdateProject,
  useDeleteProject,
  useAddSocialLink,
  useUpdateSocialLink,
  useDeleteSocialLink,
  useAddCertification,
  useUpdateCertification,
  useDeleteCertification,
  useAddLanguage,
  useUpdateLanguage,
  useDeleteLanguage,
} from "../hooks/useProfileEntities";
import { ProfileSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

type Tab = "experience" | "education" | "projects" | "certifications" | "languages" | "social-links";

const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: "experience", label: "Experience", icon: Briefcase },
  { key: "education", label: "Education", icon: BookOpen },
  { key: "projects", label: "Projects", icon: FolderGit2 },
  { key: "certifications", label: "Certifications", icon: BadgeCheck },
  { key: "languages", label: "Languages", icon: Languages },
  { key: "social-links", label: "Social Links", icon: Globe },
];

// ─── Shared form state ─────────────────────────────────────

interface ExperienceForm {
  company_name: string;
  job_title: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  description: string;
  achievements: string;
  skills_used: string;
}

const emptyExperienceForm: ExperienceForm = {
  company_name: "",
  job_title: "",
  location: "",
  start_date: "",
  end_date: "",
  is_current: false,
  description: "",
  achievements: "",
  skills_used: "",
};

interface EducationForm {
  institution: string;
  degree: string;
  field_of_study: string;
  grade: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  description: string;
  activities: string;
}

const emptyEducationForm: EducationForm = {
  institution: "",
  degree: "",
  field_of_study: "",
  grade: "",
  start_date: "",
  end_date: "",
  is_current: false,
  description: "",
  activities: "",
};

interface ProjectForm {
  name: string;
  description: string;
  url: string;
  technologies: string;
  role: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  highlights: string;
}

const emptyProjectForm: ProjectForm = {
  name: "",
  description: "",
  url: "",
  technologies: "",
  role: "",
  start_date: "",
  end_date: "",
  is_current: false,
  highlights: "",
};

// ─── Component ─────────────────────────────────────────────

export default function ProfileManagePage() {
  useDocumentTitle("Manage Profile");
  const { user } = useAuth();
  const {
    data: profile,
    isLoading,
    isError,
    error,
    refetch,
  } = useProfile(user?.id ?? "");

  const [activeTab, setActiveTab] = useState<Tab>("experience");

  // ── Experience state ──
  const [showExpForm, setShowExpForm] = useState(false);
  const [editingExpId, setEditingExpId] = useState<string | null>(null);
  const [expForm, setExpForm] = useState<ExperienceForm>(emptyExperienceForm);
  const [expError, setExpError] = useState<string | null>(null);
  const addExp = useAddExperience();
  const updateExp = useUpdateExperience();
  const deleteExp = useDeleteExperience();

  // ── Education state ──
  const [showEduForm, setShowEduForm] = useState(false);
  const [editingEduId, setEditingEduId] = useState<string | null>(null);
  const [eduForm, setEduForm] = useState<EducationForm>(emptyEducationForm);
  const [eduError, setEduError] = useState<string | null>(null);
  const addEdu = useAddEducation();
  const updateEdu = useUpdateEducation();
  const deleteEdu = useDeleteEducation();

  // ── Project state ──
  const [showProjForm, setShowProjForm] = useState(false);
  const [editingProjId, setEditingProjId] = useState<string | null>(null);
  const [projForm, setProjForm] = useState<ProjectForm>(emptyProjectForm);
  const [projError, setProjError] = useState<string | null>(null);
  const addProj = useAddProject();
  const updateProj = useUpdateProject();
  const deleteProj = useDeleteProject();

  // ── Certification state ──
  const [showCertForm, setShowCertForm] = useState(false);
  const [editingCertId, setEditingCertId] = useState<string | null>(null);
  const [certForm, setCertForm] = useState({ name: "", issuer: "", url: "", issue_date: "", expiration_date: "", does_not_expire: false, credential_id: "", description: "" });
  const [certError, setCertError] = useState<string | null>(null);
  const addCert = useAddCertification();
  const updateCert = useUpdateCertification();
  const deleteCert = useDeleteCertification();

  // ── Language state ──
  const [showLangForm, setShowLangForm] = useState(false);
  const [editingLangId, setEditingLangId] = useState<string | null>(null);
  const [langForm, setLangForm] = useState({ name: "", proficiency: "intermediate", is_native: false });
  const [langError, setLangError] = useState<string | null>(null);
  const addLang = useAddLanguage();
  const updateLang = useUpdateLanguage();
  const deleteLang = useDeleteLanguage();

  // ── Social Link state ──
  const [showLinkForm, setShowLinkForm] = useState(false);
  const [editingLinkId, setEditingLinkId] = useState<string | null>(null);
  const [linkForm, setLinkForm] = useState({ platform: "", url: "", label: "", is_primary: false });
  const [linkError, setLinkError] = useState<string | null>(null);
  const addLink = useAddSocialLink();
  const updateLink = useUpdateSocialLink();
  const deleteLink = useDeleteSocialLink();

  const profileIsLoading = addExp.isPending || updateExp.isPending || deleteExp.isPending ||
    addEdu.isPending || updateEdu.isPending || deleteEdu.isPending ||
    addProj.isPending || updateProj.isPending || deleteProj.isPending ||
    addCert.isPending || updateCert.isPending || deleteCert.isPending ||
    addLang.isPending || updateLang.isPending || deleteLang.isPending ||
    addLink.isPending || updateLink.isPending || deleteLink.isPending;

  // ─── Experience Handlers ─────────────────────────────────

  const resetExpForm = () => {
    setExpForm(emptyExperienceForm);
    setEditingExpId(null);
    setShowExpForm(false);
    setExpError(null);
  };

  const handleEditExperience = useCallback((exp: any) => {
    setExpForm({
      company_name: exp.company_name ?? "",
      job_title: exp.title ?? exp.job_title ?? "",
      location: exp.location ?? "",
      start_date: exp.start_date ? exp.start_date.slice(0, 10) : "",
      end_date: exp.end_date ? exp.end_date.slice(0, 10) : "",
      is_current: exp.is_current ?? false,
      description: exp.description ?? "",
      achievements: (exp.achievements ?? []).join(", "),
      skills_used: (exp.technologies ?? exp.skills_used ?? []).join(", "),
    });
    setEditingExpId(exp.id);
    setShowExpForm(true);
    setExpError(null);
  }, []);

  const handleSaveExperience = async () => {
    if (!profile) return;
    setExpError(null);
    try {
      const payload = {
        company_name: expForm.company_name,
        job_title: expForm.job_title,
        location: expForm.location || undefined,
        start_date: expForm.start_date || undefined,
        end_date: expForm.is_current ? undefined : (expForm.end_date || undefined),
        is_current: expForm.is_current,
        description: expForm.description || undefined,
        achievements: expForm.achievements ? expForm.achievements.split(",").map((s) => s.trim()).filter(Boolean) : [],
        skills_used: expForm.skills_used ? expForm.skills_used.split(",").map((s) => s.trim()).filter(Boolean) : [],
      };
      if (editingExpId) {
        await updateExp.mutateAsync({ expId: editingExpId, data: payload });
      } else {
        await addExp.mutateAsync({ profileId: profile.id, data: payload });
      }
      resetExpForm();
    } catch (err) {
      setExpError(getErrorMessage(err));
    }
  };

  const handleDeleteExperience = async (expId: string) => {
    try {
      await deleteExp.mutateAsync(expId);
    } catch (err) {
      setExpError(getErrorMessage(err));
    }
  };

  // ─── Education Handlers ──────────────────────────────────

  const resetEduForm = () => {
    setEduForm(emptyEducationForm);
    setEditingEduId(null);
    setShowEduForm(false);
    setEduError(null);
  };

  const handleEditEducation = useCallback((edu: any) => {
    setEduForm({
      institution: edu.institution ?? "",
      degree: edu.degree ?? "",
      field_of_study: edu.field ?? edu.field_of_study ?? "",
      grade: edu.gpa ?? edu.grade ?? "",
      start_date: edu.start_date ? edu.start_date.slice(0, 10) : "",
      end_date: edu.end_date ? edu.end_date.slice(0, 10) : "",
      is_current: edu.is_current ?? false,
      description: edu.description ?? "",
      activities: (edu.achievements ?? edu.activities ?? []).join(", "),
    });
    setEditingEduId(edu.id);
    setShowEduForm(true);
    setEduError(null);
  }, []);

  const handleSaveEducation = async () => {
    if (!profile) return;
    setEduError(null);
    try {
      const payload = {
        institution: eduForm.institution,
        degree: eduForm.degree || undefined,
        field_of_study: eduForm.field_of_study || undefined,
        grade: eduForm.grade || undefined,
        start_date: eduForm.start_date || undefined,
        end_date: eduForm.is_current ? undefined : (eduForm.end_date || undefined),
        is_current: eduForm.is_current,
        description: eduForm.description || undefined,
        activities: eduForm.activities ? eduForm.activities.split(",").map((s) => s.trim()).filter(Boolean) : [],
      };
      if (editingEduId) {
        await updateEdu.mutateAsync({ eduId: editingEduId, data: payload });
      } else {
        await addEdu.mutateAsync({ profileId: profile.id, data: payload });
      }
      resetEduForm();
    } catch (err) {
      setEduError(getErrorMessage(err));
    }
  };

  const handleDeleteEducation = async (eduId: string) => {
    try {
      await deleteEdu.mutateAsync(eduId);
    } catch (err) {
      setEduError(getErrorMessage(err));
    }
  };

  // ─── Project Handlers ────────────────────────────────────

  const resetProjForm = () => {
    setProjForm(emptyProjectForm);
    setEditingProjId(null);
    setShowProjForm(false);
    setProjError(null);
  };

  const handleEditProject = useCallback((proj: any) => {
    setProjForm({
      name: proj.name ?? "",
      description: proj.description ?? "",
      url: proj.url ?? "",
      technologies: (proj.technologies ?? []).join(", "),
      role: proj.role ?? "",
      start_date: proj.start_date ? proj.start_date.slice(0, 10) : "",
      end_date: proj.end_date ? proj.end_date.slice(0, 10) : "",
      is_current: proj.is_current ?? false,
      highlights: (proj.highlights ?? []).join(", "),
    });
    setEditingProjId(proj.id);
    setShowProjForm(true);
    setProjError(null);
  }, []);

  const handleSaveProject = async () => {
    if (!profile) return;
    setProjError(null);
    try {
      const payload = {
        name: projForm.name,
        description: projForm.description || undefined,
        url: projForm.url || undefined,
        role: projForm.role || undefined,
        technologies: projForm.technologies ? projForm.technologies.split(",").map((s) => s.trim()).filter(Boolean) : [],
        start_date: projForm.start_date || undefined,
        end_date: projForm.is_current ? undefined : (projForm.end_date || undefined),
        is_current: projForm.is_current,
        highlights: projForm.highlights ? projForm.highlights.split(",").map((s) => s.trim()).filter(Boolean) : [],
      };
      if (editingProjId) {
        await updateProj.mutateAsync({ projId: editingProjId, data: payload });
      } else {
        await addProj.mutateAsync({ profileId: profile.id, data: payload });
      }
      resetProjForm();
    } catch (err) {
      setProjError(getErrorMessage(err));
    }
  };

  const handleDeleteProject = async (projId: string) => {
    try {
      await deleteProj.mutateAsync(projId);
    } catch (err) {
      setProjError(getErrorMessage(err));
    }
  };

  // ─── Certification Handlers ─────────────────────────────

  const resetCertForm = () => {
    setCertForm({ name: "", issuer: "", url: "", issue_date: "", expiration_date: "", does_not_expire: false, credential_id: "", description: "" });
    setEditingCertId(null);
    setShowCertForm(false);
    setCertError(null);
  };

  const handleEditCertification = useCallback((cert: any) => {
    setCertForm({
      name: cert.name ?? "",
      issuer: cert.issuer ?? "",
      url: cert.url ?? "",
      issue_date: cert.issue_date ? cert.issue_date.slice(0, 10) : "",
      expiration_date: cert.expiration_date ? cert.expiration_date.slice(0, 10) : "",
      does_not_expire: cert.does_not_expire ?? false,
      credential_id: cert.credential_id ?? "",
      description: cert.description ?? "",
    });
    setEditingCertId(cert.id);
    setShowCertForm(true);
    setCertError(null);
  }, []);

  const handleSaveCertification = async () => {
    if (!profile) return;
    setCertError(null);
    try {
      const payload = {
        name: certForm.name,
        issuer: certForm.issuer || undefined,
        url: certForm.url || undefined,
        issue_date: certForm.issue_date || undefined,
        expiration_date: certForm.does_not_expire ? undefined : (certForm.expiration_date || undefined),
        does_not_expire: certForm.does_not_expire,
        credential_id: certForm.credential_id || undefined,
        description: certForm.description || undefined,
      };
      if (editingCertId) {
        await updateCert.mutateAsync({ certId: editingCertId, data: payload });
      } else {
        await addCert.mutateAsync({ profileId: profile.id, data: payload });
      }
      resetCertForm();
    } catch (err) {
      setCertError(getErrorMessage(err));
    }
  };

  const handleDeleteCertification = async (certId: string) => {
    try {
      await deleteCert.mutateAsync(certId);
    } catch (err) {
      setCertError(getErrorMessage(err));
    }
  };

  // ─── Language Handlers ──────────────────────────────────

  const resetLangForm = () => {
    setLangForm({ name: "", proficiency: "intermediate", is_native: false });
    setEditingLangId(null);
    setShowLangForm(false);
    setLangError(null);
  };

  const handleEditLanguage = useCallback((lang: any) => {
    setLangForm({
      name: lang.name ?? "",
      proficiency: lang.proficiency ?? "intermediate",
      is_native: lang.is_native ?? false,
    });
    setEditingLangId(lang.id);
    setShowLangForm(true);
    setLangError(null);
  }, []);

  const handleSaveLanguage = async () => {
    if (!profile) return;
    setLangError(null);
    try {
      const payload = {
        name: langForm.name,
        proficiency: langForm.proficiency,
        is_native: langForm.is_native,
      };
      if (editingLangId) {
        await updateLang.mutateAsync({ langId: editingLangId, data: payload });
      } else {
        await addLang.mutateAsync({ profileId: profile.id, data: payload });
      }
      resetLangForm();
    } catch (err) {
      setLangError(getErrorMessage(err));
    }
  };

  const handleDeleteLanguage = async (langId: string) => {
    try {
      await deleteLang.mutateAsync(langId);
    } catch (err) {
      setLangError(getErrorMessage(err));
    }
  };

  // ─── Social Link Handlers ───────────────────────────────

  const resetLinkForm = () => {
    setLinkForm({ platform: "", url: "", label: "", is_primary: false });
    setEditingLinkId(null);
    setShowLinkForm(false);
    setLinkError(null);
  };

  const handleEditSocialLink = useCallback((link: any) => {
    setLinkForm({
      platform: link.platform ?? "",
      url: link.url ?? "",
      label: link.label ?? "",
      is_primary: link.is_primary ?? false,
    });
    setEditingLinkId(link.id);
    setShowLinkForm(true);
    setLinkError(null);
  }, []);

  const handleSaveSocialLink = async () => {
    if (!profile) return;
    setLinkError(null);
    try {
      const payload = {
        platform: linkForm.platform,
        url: linkForm.url,
        label: linkForm.label || undefined,
        is_primary: linkForm.is_primary,
      };
      if (editingLinkId) {
        await updateLink.mutateAsync({ linkId: editingLinkId, data: payload });
      } else {
        await addLink.mutateAsync({ profileId: profile.id, data: payload });
      }
      resetLinkForm();
    } catch (err) {
      setLinkError(getErrorMessage(err));
    }
  };

  const handleDeleteSocialLink = async (linkId: string) => {
    try {
      await deleteLink.mutateAsync(linkId);
    } catch (err) {
      setLinkError(getErrorMessage(err));
    }
  };

  // ─── Loading / Error states ──────────────────────────────

  if (isLoading) {
    return (
      <div className="animate-fade-in">
        <ProfileSkeleton />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/profile" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </div>
        <ErrorFallback message={getErrorMessage(error)} onRetry={() => refetch()} />
      </div>
    );
  }

  const experiences = profile?.work_experiences ?? [];
  const educationList = profile?.education ?? [];
  const projects = profile?.projects ?? [];
  const certifications = profile?.certifications ?? [];
  const languages = profile?.languages ?? [];
  const socialLinks = profile?.social_links ?? [];

  // ─── Render ──────────────────────────────────────────────

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/profile" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Manage Profile Data</h1>
            <p className="text-gray-500">Add and manage your career information for resume generation</p>
          </div>
        </div>
        <Link
          to="/profile/skills"
          className="flex items-center gap-2 rounded-lg bg-amber-50 px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 transition-colors"
        >
          <Award className="h-4 w-4" />
          Manage Skills
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-xl bg-gray-100 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => { setActiveTab(tab.key); setShowExpForm(false); setShowEduForm(false); setShowProjForm(false); setShowCertForm(false); setShowLangForm(false); setShowLinkForm(false); }}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              activeTab === tab.key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* ─── EXPERIENCE TAB ────────────────────────────────── */}
      {activeTab === "experience" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Work Experience ({experiences.length})
            </h2>
            {!showExpForm && (
              <button
                onClick={() => { setShowExpForm(true); setExpForm(emptyExperienceForm); setEditingExpId(null); setExpError(null); }}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Experience
              </button>
            )}
          </div>

          {expError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {expError}
            </div>
          )}

          {/* Experience form */}
          {showExpForm && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-base font-semibold text-gray-900">
                {editingExpId ? "Edit Experience" : "New Experience"}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Company *</label>
                  <input type="text" value={expForm.company_name} onChange={(e) => setExpForm((f) => ({ ...f, company_name: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Job Title *</label>
                  <input type="text" value={expForm.job_title} onChange={(e) => setExpForm((f) => ({ ...f, job_title: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Location</label>
                  <input type="text" value={expForm.location} onChange={(e) => setExpForm((f) => ({ ...f, location: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input type="checkbox" checked={expForm.is_current} onChange={(e) => setExpForm((f) => ({ ...f, is_current: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    I currently work here
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date *</label>
                  <input type="date" value={expForm.start_date} onChange={(e) => setExpForm((f) => ({ ...f, start_date: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">End Date</label>
                  <input type="date" value={expForm.end_date} onChange={(e) => setExpForm((f) => ({ ...f, end_date: e.target.value }))}
                    disabled={expForm.is_current}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea rows={3} value={expForm.description} onChange={(e) => setExpForm((f) => ({ ...f, description: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Achievements (comma-separated)</label>
                  <textarea rows={2} value={expForm.achievements} onChange={(e) => setExpForm((f) => ({ ...f, achievements: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Skills Used (comma-separated)</label>
                  <textarea rows={2} value={expForm.skills_used} onChange={(e) => setExpForm((f) => ({ ...f, skills_used: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={handleSaveExperience} disabled={profileIsLoading || !expForm.company_name || !expForm.job_title || !expForm.start_date}
                  className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  {profileIsLoading ? <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> : <Save className="h-4 w-4" />}
                  {editingExpId ? "Update" : "Save"}
                </button>
                <button onClick={resetExpForm} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Experience list */}
          {experiences.length === 0 && !showExpForm ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center">
              <Briefcase className="h-8 w-8 text-gray-300 mb-3" />
              <p className="text-sm font-medium text-gray-900">No experience added yet</p>
              <p className="mt-1 text-xs text-gray-500">Add your work history to enable resume generation</p>
            </div>
          ) : (
            <div className="space-y-3">
              {experiences.map((exp) => (
                <div key={exp.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-900">{exp.title || exp.job_title}</h4>
                      <p className="text-sm text-primary-600">{exp.company_name}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {exp.location && `${exp.location} · `}
                        {exp.start_date?.slice(0, 7) ?? ""} – {exp.is_current ? "Present" : (exp.end_date?.slice(0, 7) ?? "")}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditExperience(exp)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-primary-600 transition-colors" title="Edit">
                        <Save className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDeleteExperience(exp.id)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Delete">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  {exp.description && <p className="mt-2 text-sm text-gray-600 line-clamp-2">{exp.description}</p>}
                  {exp.achievements && exp.achievements.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {exp.achievements.slice(0, 3).map((a: string, i: number) => (
                        <span key={i} className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">{a}</span>
                      ))}
                      {exp.achievements.length > 3 && (
                        <span className="text-xs text-gray-400">+{exp.achievements.length - 3} more</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── EDUCATION TAB ─────────────────────────────────── */}
      {activeTab === "education" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Education ({educationList.length})
            </h2>
            {!showEduForm && (
              <button
                onClick={() => { setShowEduForm(true); setEduForm(emptyEducationForm); setEditingEduId(null); setEduError(null); }}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Education
              </button>
            )}
          </div>

          {eduError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {eduError}
            </div>
          )}

          {/* Education form */}
          {showEduForm && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-base font-semibold text-gray-900">
                {editingEduId ? "Edit Education" : "New Education"}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Institution *</label>
                  <input type="text" value={eduForm.institution} onChange={(e) => setEduForm((f) => ({ ...f, institution: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Degree</label>
                  <input type="text" value={eduForm.degree} onChange={(e) => setEduForm((f) => ({ ...f, degree: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Field of Study</label>
                  <input type="text" value={eduForm.field_of_study} onChange={(e) => setEduForm((f) => ({ ...f, field_of_study: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Grade / GPA</label>
                  <input type="text" value={eduForm.grade} onChange={(e) => setEduForm((f) => ({ ...f, grade: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input type="checkbox" checked={eduForm.is_current} onChange={(e) => setEduForm((f) => ({ ...f, is_current: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    Currently enrolled
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date *</label>
                  <input type="date" value={eduForm.start_date} onChange={(e) => setEduForm((f) => ({ ...f, start_date: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">End Date</label>
                  <input type="date" value={eduForm.end_date} onChange={(e) => setEduForm((f) => ({ ...f, end_date: e.target.value }))}
                    disabled={eduForm.is_current}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea rows={3} value={eduForm.description} onChange={(e) => setEduForm((f) => ({ ...f, description: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Activities (comma-separated)</label>
                  <textarea rows={2} value={eduForm.activities} onChange={(e) => setEduForm((f) => ({ ...f, activities: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={handleSaveEducation} disabled={profileIsLoading || !eduForm.institution || !eduForm.start_date}
                  className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  {profileIsLoading ? <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> : <Save className="h-4 w-4" />}
                  {editingEduId ? "Update" : "Save"}
                </button>
                <button onClick={resetEduForm} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Education list */}
          {educationList.length === 0 && !showEduForm ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center">
              <BookOpen className="h-8 w-8 text-gray-300 mb-3" />
              <p className="text-sm font-medium text-gray-900">No education added yet</p>
              <p className="mt-1 text-xs text-gray-500">Add your educational background to enhance your resume</p>
            </div>
          ) : (
            <div className="space-y-3">
              {educationList.map((edu) => (
                <div key={edu.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-900">{edu.institution}</h4>
                      <p className="text-sm text-gray-600">
                        {edu.degree}{edu.field ? ` in ${edu.field}` : ""}
                        {edu.gpa ? ` · GPA: ${edu.gpa}` : ""}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {edu.start_date?.slice(0, 7) ?? ""} – {edu.is_current ? "Present" : (edu.end_date?.slice(0, 7) ?? "")}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditEducation(edu)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-primary-600 transition-colors" title="Edit">
                        <Save className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDeleteEducation(edu.id)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Delete">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  {edu.description && <p className="mt-2 text-sm text-gray-600 line-clamp-2">{edu.description}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── PROJECTS TAB ──────────────────────────────────── */}
      {activeTab === "projects" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Projects ({projects.length})
            </h2>
            {!showProjForm && (
              <button
                onClick={() => { setShowProjForm(true); setProjForm(emptyProjectForm); setEditingProjId(null); setProjError(null); }}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Project
              </button>
            )}
          </div>

          {projError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {projError}
            </div>
          )}

          {/* Project form */}
          {showProjForm && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-base font-semibold text-gray-900">
                {editingProjId ? "Edit Project" : "New Project"}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Project Name *</label>
                  <input type="text" value={projForm.name} onChange={(e) => setProjForm((f) => ({ ...f, name: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">URL</label>
                  <input type="url" value={projForm.url} onChange={(e) => setProjForm((f) => ({ ...f, url: e.target.value }))}
                    placeholder="https://github.com/..." className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea rows={3} value={projForm.description} onChange={(e) => setProjForm((f) => ({ ...f, description: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <input type="text" value={projForm.role} onChange={(e) => setProjForm((f) => ({ ...f, role: e.target.value }))}
                    placeholder="e.g., Lead Developer" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input type="checkbox" checked={projForm.is_current} onChange={(e) => setProjForm((f) => ({ ...f, is_current: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    Ongoing project
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input type="date" value={projForm.start_date} onChange={(e) => setProjForm((f) => ({ ...f, start_date: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">End Date</label>
                  <input type="date" value={projForm.end_date} onChange={(e) => setProjForm((f) => ({ ...f, end_date: e.target.value }))}
                    disabled={projForm.is_current}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Technologies (comma-separated)</label>
                  <input type="text" value={projForm.technologies} onChange={(e) => setProjForm((f) => ({ ...f, technologies: e.target.value }))}
                    placeholder="React, TypeScript, Node.js" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Highlights (comma-separated)</label>
                  <textarea rows={2} value={projForm.highlights} onChange={(e) => setProjForm((f) => ({ ...f, highlights: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={handleSaveProject} disabled={profileIsLoading || !projForm.name}
                  className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  {profileIsLoading ? <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" /> : <Save className="h-4 w-4" />}
                  {editingProjId ? "Update" : "Save"}
                </button>
                <button onClick={resetProjForm} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Project list */}
          {projects.length === 0 && !showProjForm ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center">
              <FolderGit2 className="h-8 w-8 text-gray-300 mb-3" />
              <p className="text-sm font-medium text-gray-900">No projects added yet</p>
              <p className="mt-1 text-xs text-gray-500">Showcase your projects to make your resume stand out</p>
            </div>
          ) : (
            <div className="space-y-3">
              {projects.map((proj) => (
                <div key={proj.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-gray-900">{proj.name}</h4>
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-primary-600">
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        )}
                      </div>
                      {proj.role && <p className="text-sm text-gray-500">{proj.role}</p>}
                      <p className="text-xs text-gray-400 mt-1">
                        {proj.start_date?.slice(0, 7) ?? ""} – {proj.is_current ? "Present" : (proj.end_date?.slice(0, 7) ?? "")}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditProject(proj)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-primary-600 transition-colors" title="Edit">
                        <Save className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDeleteProject(proj.id)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Delete">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  {proj.description && <p className="mt-2 text-sm text-gray-600 line-clamp-2">{proj.description}</p>}
                  {proj.technologies && proj.technologies.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {proj.technologies.map((tech) => (
                        <span key={tech} className="rounded-full bg-purple-50 px-2 py-0.5 text-xs text-purple-700">{tech}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── CERTIFICATIONS TAB ────────────────────────────── */}
      {activeTab === "certifications" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Certifications ({certifications.length})
            </h2>
            {!showCertForm && (
              <button
                onClick={() => { setShowCertForm(true); setCertForm({ name: "", issuer: "", url: "", issue_date: "", expiration_date: "", does_not_expire: false, credential_id: "", description: "" }); setEditingCertId(null); setCertError(null); }}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Certification
              </button>
            )}
          </div>

          {certError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {certError}
            </div>
          )}

          {showCertForm && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-base font-semibold text-gray-900">
                {editingCertId ? "Edit Certification" : "New Certification"}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Certification Name *</label>
                  <input type="text" value={certForm.name} onChange={(e) => setCertForm((f) => ({ ...f, name: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Issuer</label>
                  <input type="text" value={certForm.issuer} onChange={(e) => setCertForm((f) => ({ ...f, issuer: e.target.value }))}
                    placeholder="e.g., AWS, Google, Microsoft" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Credential ID</label>
                  <input type="text" value={certForm.credential_id} onChange={(e) => setCertForm((f) => ({ ...f, credential_id: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Issue Date</label>
                  <input type="date" value={certForm.issue_date} onChange={(e) => setCertForm((f) => ({ ...f, issue_date: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Expiration Date</label>
                  <input type="date" value={certForm.expiration_date} onChange={(e) => setCertForm((f) => ({ ...f, expiration_date: e.target.value }))}
                    disabled={certForm.does_not_expire}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50" />
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input type="checkbox" checked={certForm.does_not_expire} onChange={(e) => setCertForm((f) => ({ ...f, does_not_expire: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    Does not expire
                  </label>
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">URL</label>
                  <input type="url" value={certForm.url} onChange={(e) => setCertForm((f) => ({ ...f, url: e.target.value }))}
                    placeholder="https://credential.example.com/..." className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea rows={2} value={certForm.description} onChange={(e) => setCertForm((f) => ({ ...f, description: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={handleSaveCertification} disabled={profileIsLoading || !certForm.name}
                  className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  <Save className="h-4 w-4" />
                  {editingCertId ? "Update" : "Save"}
                </button>
                <button onClick={resetCertForm} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {certifications.length === 0 && !showCertForm ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center">
              <BadgeCheck className="h-8 w-8 text-gray-300 mb-3" />
              <p className="text-sm font-medium text-gray-900">No certifications added yet</p>
              <p className="mt-1 text-xs text-gray-500">Add professional certifications to boost your resume</p>
            </div>
          ) : (
            <div className="space-y-3">
              {certifications.map((cert) => (
                <div key={cert.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-900">{cert.name}</h4>
                      {cert.issuer && <p className="text-sm text-gray-600">{cert.issuer}</p>}
                      <p className="text-xs text-gray-400 mt-1">
                        {cert.issue_date?.slice(0, 7) ?? ""}{cert.issuer ? ` · ${cert.issuer}` : ""}
                        {cert.credential_id ? ` · ID: ${cert.credential_id}` : ""}
                      </p>
                      {cert.url && (
                        <a href={cert.url} target="_blank" rel="noopener noreferrer" className="mt-1 inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-500">
                          View credential <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditCertification(cert)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-primary-600 transition-colors" title="Edit">
                        <Save className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDeleteCertification(cert.id)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Delete">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  {cert.description && <p className="mt-2 text-sm text-gray-600 line-clamp-2">{cert.description}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── LANGUAGES TAB ─────────────────────────────────── */}
      {activeTab === "languages" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Languages ({languages.length})
            </h2>
            {!showLangForm && (
              <button
                onClick={() => { setShowLangForm(true); setLangForm({ name: "", proficiency: "intermediate", is_native: false }); setEditingLangId(null); setLangError(null); }}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Language
              </button>
            )}
          </div>

          {langError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {langError}
            </div>
          )}

          {showLangForm && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-base font-semibold text-gray-900">
                {editingLangId ? "Edit Language" : "New Language"}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Language *</label>
                  <input type="text" value={langForm.name} onChange={(e) => setLangForm((f) => ({ ...f, name: e.target.value }))}
                    placeholder="e.g., English, Spanish, French" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Proficiency</label>
                  <select value={langForm.proficiency} onChange={(e) => setLangForm((f) => ({ ...f, proficiency: e.target.value }))}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="native">Native</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input type="checkbox" checked={langForm.is_native} onChange={(e) => setLangForm((f) => ({ ...f, is_native: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    Native language
                  </label>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={handleSaveLanguage} disabled={profileIsLoading || !langForm.name}
                  className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  <Save className="h-4 w-4" />
                  {editingLangId ? "Update" : "Save"}
                </button>
                <button onClick={resetLangForm} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {languages.length === 0 && !showLangForm ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center">
              <Languages className="h-8 w-8 text-gray-300 mb-3" />
              <p className="text-sm font-medium text-gray-900">No languages added yet</p>
              <p className="mt-1 text-xs text-gray-500">Add languages to enhance your resume for global roles</p>
            </div>
          ) : (
            <div className="space-y-3">
              {languages.map((lang) => (
                <div key={lang.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-pink-400 to-rose-500 text-sm font-bold text-white">
                        {lang.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{lang.name}</h4>
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          lang.proficiency === "native" ? "bg-green-100 text-green-700" :
                          lang.proficiency === "advanced" ? "bg-blue-100 text-blue-700" :
                          lang.proficiency === "intermediate" ? "bg-yellow-100 text-yellow-700" :
                          "bg-gray-100 text-gray-600"
                        }`}>
                          {lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)}
                        </span>
                        {lang.is_native && <span className="ml-1 text-xs text-gray-400">(Native)</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditLanguage(lang)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-primary-600 transition-colors" title="Edit">
                        <Save className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDeleteLanguage(lang.id)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Delete">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ─── SOCIAL LINKS TAB ──────────────────────────────── */}
      {activeTab === "social-links" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Social Links ({socialLinks.length})
            </h2>
            {!showLinkForm && (
              <button
                onClick={() => { setShowLinkForm(true); setLinkForm({ platform: "", url: "", label: "", is_primary: false }); setEditingLinkId(null); setLinkError(null); }}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Link
              </button>
            )}
          </div>

          {linkError && (
            <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {linkError}
            </div>
          )}

          {showLinkForm && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-base font-semibold text-gray-900">
                {editingLinkId ? "Edit Social Link" : "New Social Link"}
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Platform *</label>
                  <input type="text" value={linkForm.platform} onChange={(e) => setLinkForm((f) => ({ ...f, platform: e.target.value }))}
                    placeholder="e.g., LinkedIn, GitHub, Twitter" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Label</label>
                  <input type="text" value={linkForm.label} onChange={(e) => setLinkForm((f) => ({ ...f, label: e.target.value }))}
                    placeholder="e.g., Personal blog" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">URL *</label>
                  <input type="url" value={linkForm.url} onChange={(e) => setLinkForm((f) => ({ ...f, url: e.target.value }))}
                    placeholder="https://linkedin.com/in/..." className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500" />
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input type="checkbox" checked={linkForm.is_primary} onChange={(e) => setLinkForm((f) => ({ ...f, is_primary: e.target.checked }))}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    Primary link
                  </label>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button onClick={handleSaveSocialLink} disabled={profileIsLoading || !linkForm.platform || !linkForm.url}
                  className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors">
                  <Save className="h-4 w-4" />
                  {editingLinkId ? "Update" : "Save"}
                </button>
                <button onClick={resetLinkForm} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {socialLinks.length === 0 && !showLinkForm ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-12 text-center">
              <Globe className="h-8 w-8 text-gray-300 mb-3" />
              <p className="text-sm font-medium text-gray-900">No social links added yet</p>
              <p className="mt-1 text-xs text-gray-500">Add your professional profiles and personal websites</p>
            </div>
          ) : (
            <div className="space-y-3">
              {socialLinks.map((link) => (
                <div key={link.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-400 to-purple-600 text-sm font-bold text-white">
                        {link.platform.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{link.label || link.platform}</h4>
                        <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary-600 hover:text-primary-500 hover:underline">
                          {link.url.replace(/^https?:\/\//, "")}
                        </a>
                        {link.is_primary && (
                          <span className="ml-2 inline-flex items-center rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">Primary</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEditSocialLink(link)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-primary-600 transition-colors" title="Edit">
                        <Save className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDeleteSocialLink(link.id)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-red-600 transition-colors" title="Delete">
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
