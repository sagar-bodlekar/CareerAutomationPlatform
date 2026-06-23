import { useState, useEffect, useRef } from "react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
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
  gender: string;
  pronouns: string;
}

const GENDER_OPTIONS = ["Male", "Female", "Non-binary", "Prefer not to say"];

const emptyForm: FormState = {
  full_name: "",
  email: "",
  phone: "",
  location: "",
  headline: "",
  summary: "",
  gender: "",
  pronouns: "",
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

  useDocumentTitle("Edit Profile");

  const formRef = useRef<HTMLFormElement>(null);

  const [form, setForm] = useState<FormState>(emptyForm);
  const [saveVersion, setSaveVersion] = useState(0); // Incremented after each save to trigger form refresh

  // Initialize / refresh form from profile data (on load AND after save)
  // Uses profile?.id (stable) instead of profile (unstable ref) to avoid
  // resetting unsaved edits during background refetches
  useEffect(() => {
    if (profile) {
      const pi = profile.personal_info;
      setForm({
        full_name: pi?.full_name ?? "",
        email: pi?.email ?? "",
        phone: pi?.phone ?? "",
        location: pi?.city ?? pi?.location ?? "",
        headline: profile.headline ?? "",
        summary: profile.summary ?? "",
        gender: pi?.gender ?? "",
        pronouns: pi?.pronouns ?? "",
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile?.id, saveVersion]);

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
        gender: form.gender || undefined,
        pronouns: form.pronouns || undefined,
      },
    };

    try {
      if (!profile) {
        // No profile yet — create one first
        await createProfileMutation.mutateAsync({
          userId: user?.id ?? "",
          data: payload as Partial<Profile>,
        });
      } else {
        // Profile exists — update it
        await updateProfileMutation.mutateAsync({
          profileId: profile.id,
          data: payload as Partial<Profile>,
        });
      }
      // Re-populate form with saved data (triggers the useEffect above)
      setSaveVersion((v) => v + 1);
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
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link to="/profile" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Edit Profile</h1>
            <p className="text-gray-500">Update your career information</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => formRef.current?.requestSubmit()}
          disabled={isSaving}
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 disabled:opacity-50"
        >
          {isSaving ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          {isSaving ? "Saving..." : "Save Changes"}
        </button>
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

      <form ref={formRef} onSubmit={handleSave} className="space-y-6">
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
              <label className="block text-sm font-medium text-gray-700">Mobile Number</label>
              <input
                type="tel"
                value={form.phone}
                onChange={handleChange("phone")}
                placeholder="+1-555-0100"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Gender</label>
              <select
                value={form.gender}
                onChange={(e) => setForm((prev) => ({ ...prev, gender: e.target.value }))}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                <option value="">Select gender</option>
                {GENDER_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Pronouns</label>
              <input
                type="text"
                value={form.pronouns}
                onChange={handleChange("pronouns")}
                placeholder="e.g., they/them, she/her, he/him"
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

        <p className="text-xs text-gray-400 -mt-4">
          Manage your social links (LinkedIn, GitHub, etc.) in the{' '}
          <Link to="/profile/manage" className="text-primary-600 hover:text-primary-500 underline">Manage Profile Data</Link> section.
        </p>

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
