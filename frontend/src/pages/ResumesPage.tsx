import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { Link } from "react-router-dom";
import { FileText, Plus } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useResumes } from "../hooks/useResumes";
import { useProfile } from "../hooks/useProfile";
import ResumeCard from "../components/resumes/ResumeCard";
import { CardSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

export default function ResumesPage() {
  useDocumentTitle("Resumes");
  const { user } = useAuth();
  const { data: profile } = useProfile(user?.id ?? "");
  const profileId = profile?.id ?? "";

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useResumes(profileId);

  const resumes = data?.data ?? [];

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resumes</h1>
          <p className="text-gray-500">Create and manage your role-specific resumes</p>
        </div>
        <Link
          to="/resumes/generate"
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700"
        >
          <Plus className="h-4 w-4" />
          Generate Resume
        </Link>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {/* Error state */}
      {!isLoading && isError && (
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      )}

      {/* Empty state */}
      {!isLoading && !isError && resumes.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-16 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 mb-4">
            <FileText className="h-6 w-6 text-indigo-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">No resumes yet</h3>
          <p className="mt-1 text-sm text-gray-500 max-w-sm">
            Generate your first resume from your profile data and choose a template that showcases your skills.
          </p>
          <Link
            to="/resumes/generate"
            className="mt-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
          >
            Generate Your First Resume
          </Link>
        </div>
      )}

      {/* Resume cards */}
      {!isLoading && !isError && resumes.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {resumes.map((resume) => (
            <ResumeCard key={resume.id} resume={resume} />
          ))}
        </div>
      )}
    </div>
  );
}
