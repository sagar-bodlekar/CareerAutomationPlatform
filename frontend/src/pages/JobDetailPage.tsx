import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, MapPin, Briefcase, Clock, ExternalLink, Send, BarChart3, DollarSign, AlertCircle } from "lucide-react";
import { useJob } from "../hooks/useJobs";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useAuth } from "../context/AuthContext";
import { useJobMatch } from "../hooks/useJobMatch";
import { useCreateApplication } from "../hooks/useApplications";
import { useProfile } from "../hooks/useProfile";
import { JobDetailSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { formatSalary, formatRelativeTime, getScoreLabel } from "../utils/formatters";
import { getErrorMessage } from "../utils/errorHandler";

export default function JobDetailPage() {
  useDocumentTitle("Job Details");
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: profile } = useProfile(user?.id ?? "");
  const profileId = profile?.id ?? "";
  const jobId = Number(id);

  const {
    data: job,
    isLoading,
    isError,
    error,
    refetch,
  } = useJob(jobId);

  const { data: match, isLoading: matchLoading } = useJobMatch(profileId, jobId);

  const createApplication = useCreateApplication();
  const [applying, setApplying] = useState(false);

  const handleApply = async () => {
    if (!job) return;
    setApplying(true);
    try {
      await createApplication.mutateAsync({
        profile_id: profileId,
        job_id: job.id,
        company_name: job.company_name,
        job_title: job.title,
        match_score: match?.match_score,
      });
      navigate("/applications");
    } catch (err) {
      // Error state is handled by the mutation's error
    } finally {
      setApplying(false);
    }
  };

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in">
        <JobDetailSkeleton />
      </div>
    );
  }

  // --- Error state ---
  if (isError) {
    return (
      <div className="animate-fade-in space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" /> Back to jobs
        </button>
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  // --- Not found state ---
  if (!job) {
    return (
      <div className="animate-fade-in space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" /> Back to jobs
        </button>
        <div className="flex flex-col items-center justify-center rounded-xl border bg-white p-12 shadow-sm">
          <AlertCircle className="mb-4 h-12 w-12 text-gray-300" />
          <h2 className="mb-2 text-lg font-semibold text-gray-900">Job not found</h2>
          <p className="mb-6 text-sm text-gray-500">This job listing may have been removed or is no longer available.</p>
          <Link to="/jobs" className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700">
            Browse Jobs
          </Link>
        </div>
      </div>
    );
  }

  // --- Populated state ---
  const companyInitials = job.company_name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const requirementsList = job.requirements
    ? job.requirements.split("\n").filter(Boolean)
    : [];

  const matchScore = match?.match_score;
  const applyError = createApplication.isError ? getErrorMessage(createApplication.error) : null;

  return (
    <div className="animate-fade-in space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to jobs
      </button>

      {/* Header card */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 text-xl font-bold text-white shadow-md">
              {companyInitials}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
              <p className="text-lg text-gray-500">{job.company_name}</p>
              <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                {job.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" /> {job.location}
                  </span>
                )}
                {job.employment_type && (
                  <span className="flex items-center gap-1">
                    <Briefcase className="h-4 w-4" /> {job.employment_type.replace(/_/g, "-")}
                  </span>
                )}
                {(job.salary_min || job.salary_max) && (
                  <span className="flex items-center gap-1">
                    <DollarSign className="h-4 w-4" /> {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
                  </span>
                )}
                {job.posted_at && (
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" /> {formatRelativeTime(job.posted_at)}
                  </span>
                )}
              </div>
            </div>
          </div>
          {matchScore !== undefined && (
            <div className="flex flex-col items-center gap-1">
              <div
                className={`flex h-16 w-16 items-center justify-center rounded-full ${
                  matchScore >= 85
                    ? "bg-green-50"
                    : matchScore >= 70
                    ? "bg-blue-50"
                    : "bg-amber-50"
                }`}
              >
                <span
                  className={`text-xl font-bold ${
                    matchScore >= 85
                      ? "text-green-600"
                      : matchScore >= 70
                      ? "text-blue-600"
                      : "text-amber-600"
                  }`}
                >
                  {matchScore}%
                </span>
              </div>
              <span className="text-xs text-gray-400">
                {matchLoading ? "Loading..." : getScoreLabel(matchScore).split(" ")[0]}
              </span>
            </div>
          )}
          {matchLoading && !matchScore && (
            <div className="flex flex-col items-center gap-1">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-50 animate-pulse" />
              <span className="text-xs text-gray-300">Match</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* Description */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Description</h2>
            <p className="whitespace-pre-line text-sm text-gray-600">{job.description}</p>
          </div>

          {/* Requirements */}
          {requirementsList.length > 0 && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h2 className="mb-3 text-lg font-semibold text-gray-900">Requirements</h2>
              {job.experience_level && (
                <p className="mb-3 text-sm font-medium text-gray-500">{job.experience_level} level</p>
              )}
              <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
                {requirementsList.map((req, i) => (
                  <li key={i}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Preferred Skills */}
          {job.nice_to_have_skills && job.nice_to_have_skills.length > 0 && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h2 className="mb-3 text-lg font-semibold text-gray-900">Nice-to-Have Skills</h2>
              <div className="flex flex-wrap gap-2">
                {job.nice_to_have_skills.map((skill) => (
                  <span key={skill} className="rounded-full bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-semibold text-gray-900">Actions</h3>
            <div className="space-y-3">
              <button
                onClick={handleApply}
                disabled={applying || createApplication.isPending}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 disabled:opacity-50"
              >
                {applying || createApplication.isPending ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {applying || createApplication.isPending ? "Creating application..." : "Apply Now"}
              </button>
              {applyError && (
                <p className="text-xs text-red-600">{applyError}</p>
              )}
              {match && (
                <Link
                  to={`/jobs/${job.id}/matches`}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                >
                  <BarChart3 className="h-4 w-4" />
                  View Match Details
                </Link>
              )}
              {job.source_url && (
                <a
                  href={job.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
                >
                  <ExternalLink className="h-4 w-4" />
                  View Original Posting
                </a>
              )}
            </div>
          </div>

          {/* Required Skills */}
          {job.required_skills && job.required_skills.length > 0 && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-3 font-semibold text-gray-900">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
