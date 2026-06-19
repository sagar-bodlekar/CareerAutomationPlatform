import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Save, ArrowLeft, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useProfile, useCreateProfile, useUpdateProfile } from "../hooks/useProfile";
import { ProfileSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage, isNotFoundError } from "../utils/errorHandler";
import type { Profile } from "../types";

interface FormState {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  headline: string;
  summary: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  website_url: string;
}

const emptyForm: FormState = {
  full_name: "",
  email: "",
  phone: "",
  location: "",
  headline: "",
  summary: "",
  linkedin_url: "",
  github_url: "",
  portfolio_url: "",
  website_url: "",
};

export default function ProfileEditPage() {
  const { user } = useAuth();
  const {
    data: profile,
    isLoading,
    isError,
    error,
    refetch,
  } = useProfile(user?.id ?? "");

  const updateProfileMutation = useUpdateProfile();
  const createProfileMutation = useCreateProfile();

  const [form, setForm] = useState<FormState>(emptyForm);
  const [initialized, setInitialized] = useState(false);

  // Initialize form from profile data
  useEffect(() => {
    if (profile && !initialized) {
      const pi = profile.personal_info;
      setForm({
        full_name: pi?.full_name ?? "",
        email: pi?.email ?? "",
        phone: pi?.phone ?? "",
        location: pi?.city ?? pi?.location ?? "",
        headline: profile.headline ?? "",
        summary: profile.summary ?? "",
        linkedin_url: pi?.linkedin_url ?? "",
        github_url: pi?.github_url ?? "",
        portfolio_url: pi?.portfolio_url ?? "",
        website_url: pi?.website_url ?? "",
      });
      setInitialized(true);
    }
  }, [profile, initialized]);

  const [saveError, setSaveError] = useState<string | null>(null);

  const handleChange = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveError(null);

    const payload: Record<string, unknown> = {
      headline: form.headline || undefined,
      summary: form.summary || undefined,
      personal_info: {
        full_name: form.full_name,
        email: form.email,
        phone: form.phone || undefined,
        city: form.location || undefined,
      },
    };

    try {
      if (!profile) {
        // No profile yet — create one first
        await createProfileMutation.mutateAsync({
          userId: user?.id ?? "",
          data: payload as Partial<Profile>,
        });
        // The refetch happens automatically via invalidateQueries
      } else {
        // Profile exists — update it
        await updateProfileMutation.mutateAsync({
          profileId: profile.id,
          data: payload as Partial<Profile>,
        });
      }
    } catch (err) {
      setSaveError(getErrorMessage(err));
    }
  };

  const isSaving = updateProfileMutation.isPending || createProfileMutation.isPending;

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in">
        <ProfileSkeleton />
      </div>
    );
  }

  // --- Error state (non-404 errors only) ---
  if (isError && !isNotFoundError(error)) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/profile" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </div>
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  // --- Populated state (also reached on 404 — shows empty form for new users) ---
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/profile" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Edit Profile</h1>
            <p className="text-gray-500">Update your career information</p>
          </div>
        </div>
      </div>

      {saveError && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {saveError}
        </div>
      )}

      {(updateProfileMutation.isSuccess || createProfileMutation.isSuccess) && !saveError && (
        <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
          Profile saved successfully!
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Personal Info */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Personal Information</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">Full name *</label>
              <input
                type="text"
                value={form.full_name}
                onChange={handleChange("full_name")}
                required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={handleChange("email")}
                required
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <input
                type="tel"
                value={form.phone}
                onChange={handleChange("phone")}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <input
                type="text"
                value={form.location}
                onChange={handleChange("location")}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Headline</label>
              <input
                type="text"
                value={form.headline}
                onChange={handleChange("headline")}
                placeholder="e.g., Senior Full Stack Engineer"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Summary</label>
              <textarea
                rows={3}
                value={form.summary}
                onChange={handleChange("summary")}
                placeholder="A brief professional summary..."
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Social Links */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Social Links</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">LinkedIn URL</label>
              <input
                type="url"
                value={form.linkedin_url}
                onChange={handleChange("linkedin_url")}
                placeholder="https://linkedin.com/in/..."
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">GitHub URL</label>
              <input
                type="url"
                value={form.github_url}
                onChange={handleChange("github_url")}
                placeholder="https://github.com/..."
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Portfolio URL</label>
              <input
                type="url"
                value={form.portfolio_url}
                onChange={handleChange("portfolio_url")}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Website</label>
              <input
                type="url"
                value={form.website_url}
                onChange={handleChange("website_url")}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Submit button inside form */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="flex items-center gap-2 rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 disabled:opacity-50"
          >
            {isSaving ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {isSaving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
