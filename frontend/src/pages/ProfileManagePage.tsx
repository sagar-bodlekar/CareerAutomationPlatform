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
} from "lucide-react";
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
} from "../hooks/useProfileEntities";
import { ProfileSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

type Tab = "experience" | "education" | "projects";

const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: "experience", label: "Experience", icon: Briefcase },
  { key: "education", label: "Education", icon: BookOpen },
  { key: "projects", label: "Projects", icon: FolderGit2 },
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

  const profileIsLoading = addExp.isPending || updateExp.isPending || deleteExp.isPending ||
    addEdu.isPending || updateEdu.isPending || deleteEdu.isPending ||
    addProj.isPending || updateProj.isPending || deleteProj.isPending;

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
            onClick={() => { setActiveTab(tab.key); setShowExpForm(false); setShowEduForm(false); setShowProjForm(false); }}
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
    </div>
  );
}
