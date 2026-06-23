import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { Plus, Search, X, Award, Save, AlertCircle } from "lucide-react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useAuth } from "../context/AuthContext";
import { useProfile } from "../hooks/useProfile";
import { useDeleteSkill, useBulkAddSkills } from "../hooks/useProfileEntities";
import { ProfileSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";
import type { Skill } from "../types";

// Suggestion pool of common skills (no backend catalog available)
const allSkills = [
  { name: "Python", category: "technical" },
  { name: "React", category: "technical" },
  { name: "TypeScript", category: "technical" },
  { name: "JavaScript", category: "technical" },
  { name: "AWS", category: "technical" },
  { name: "Docker", category: "technical" },
  { name: "PostgreSQL", category: "technical" },
  { name: "GraphQL", category: "technical" },
  { name: "Node.js", category: "technical" },
  { name: "Go", category: "technical" },
  { name: "Rust", category: "technical" },
  { name: "Kubernetes", category: "technical" },
  { name: "Leadership", category: "soft" },
  { name: "Communication", category: "soft" },
  { name: "Project Management", category: "soft" },
  { name: "Mentoring", category: "soft" },
  { name: "Machine Learning", category: "domain" },
  { name: "Data Engineering", category: "domain" },
  { name: "DevOps", category: "domain" },
];

function Badge({ children, color }: { children: React.ReactNode; color?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${color || "bg-gray-100 text-gray-700"}`}>
      {children}
    </span>
  );
}

export default function SkillsPage() {
  useDocumentTitle("Skills");
  const { user } = useAuth();
  const {
    data: profile,
    isLoading,
    isError,
    error,
    refetch,
  } = useProfile(user?.id ?? "");

  const deleteSkill = useDeleteSkill();
  const bulkAdd = useBulkAddSkills();

  const [search, setSearch] = useState("");
  const [mySkills, setMySkills] = useState<Skill[]>([]);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Initialize local skills state from profile data
  useEffect(() => {
    if (profile?.skills) {
      setMySkills(profile.skills);
      setHasChanges(false);
    }
  }, [profile?.skills]);

  const addSkill = useCallback((name: string) => {
    const candidate = allSkills.find((s) => s.name === name);
    if (!candidate) return;
    const newSkill: Skill = {
      id: "", // New skill, backend will assign id
      name: candidate.name,
      category: candidate.category,
      proficiency: "intermediate",
      years_experience: undefined,
      is_top_skill: false,
    };
    setMySkills((prev) => [...prev, newSkill]);
    setHasChanges(true);
  }, []);

  const removeSkill = useCallback((name: string) => {
    setMySkills((prev) => prev.filter((s) => s.name !== name));
    setHasChanges(true);
  }, []);

  const setProficiency = useCallback((name: string, proficiency: string) => {
    setMySkills((prev) => prev.map((s) => (s.name === name ? { ...s, proficiency } : s)));
    setHasChanges(true);
  }, []);

  const isSaving = deleteSkill.isPending || bulkAdd.isPending;

  const handleSave = async () => {
    if (!profile) return;
    setSaveError(null);
    try {
      // Step 1: Delete all existing skills
      const existingSkills = profile.skills ?? [];
      const deletePromises = existingSkills
        .filter((s) => s.id !== "")
        .map((s) => deleteSkill.mutateAsync(s.id));
      await Promise.all(deletePromises);

      // Step 2: Bulk add the new skill set
      if (mySkills.length > 0) {
        await bulkAdd.mutateAsync({
          profileId: profile.id,
          skills: mySkills.map((s) => ({
            name: s.name,
            category: s.category,
            proficiency: s.proficiency,
          })),
        });
      }

      setHasChanges(false);
    } catch (err) {
      setSaveError(getErrorMessage(err));
    }
  };

  const suggestedSkills = allSkills.filter(
    (s) => s.name.toLowerCase().includes(search.toLowerCase()) && !mySkills.find((ms) => ms.name === s.name)
  );

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in">
        <ProfileSkeleton />
      </div>
    );
  }

  // --- Error state ---
  if (isError) {
    return (
      <div className="animate-fade-in space-y-6">
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  // --- Populated state ---
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
            <Award className="h-6 w-6 text-amber-500" /> Skills
          </h1>
          <p className="text-gray-500">Manage your skills and proficiencies</p>
        </div>
        <div className="flex items-center gap-3">
          {hasChanges && (
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {isSaving ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          )}
          <Link to="/profile" className="text-sm font-medium text-gray-500 hover:text-gray-700">
            ← Back to Profile
          </Link>
        </div>
      </div>

      {saveError && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {saveError}
        </div>
      )}

      {/* My skills */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Your Skills ({mySkills.length})</h2>
        {mySkills.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {mySkills.map((skill) => (
              <Badge
                key={skill.name}
                color={
                  skill.proficiency === "expert"
                    ? "bg-purple-100 text-purple-700"
                    : skill.proficiency === "advanced"
                    ? "bg-blue-100 text-blue-700"
                    : "bg-green-100 text-green-700"
                }
              >
                {skill.name}
                <select
                  value={skill.proficiency}
                  onChange={(e) => setProficiency(skill.name, e.target.value)}
                  className="ml-1 text-xs bg-transparent border-none outline-none cursor-pointer"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
                <button onClick={() => removeSkill(skill.name)} className="ml-1 hover:text-red-500 transition-colors">
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        ) : (
          <p className="py-6 text-center text-sm text-gray-400">
            No skills added yet. Use the section below to search and add skills.
          </p>
        )}
      </div>

      {/* Add skills */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Add Skills</h2>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search skills..."
            className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {suggestedSkills.map((skill) => (
            <button
              key={skill.name}
              onClick={() => addSkill(skill.name)}
              className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700 transition-colors hover:bg-primary-100 hover:text-primary-700"
            >
              <Plus className="h-3 w-3" />
              {skill.name}
              <span className="text-gray-400">({skill.category})</span>
            </button>
          ))}
          {suggestedSkills.length === 0 && (
            <p className="w-full py-4 text-center text-sm text-gray-400">
              {search ? "No skills found" : "All suggested skills have been added"}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
