import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Send, Building2, FileText, Mail, AlertCircle, CheckCircle2, XCircle } from "lucide-react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useApplication, useSubmitApplication } from "../hooks/useApplications";
import { useApplicationEvents } from "../hooks/useApplicationEvents";
import { ApplicationDetailSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import StatusBadge from "../components/applications/StatusBadge";
import TimelineView from "../components/applications/TimelineView";
import { formatDate, capitalize } from "../utils/formatters";
import { getErrorMessage } from "../utils/errorHandler";

export default function ApplicationDetailPage() {
  useDocumentTitle("Application Details");
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const appId = Number(id);

  const {
    data: application,
    isLoading,
    isError,
    error,
    refetch,
  } = useApplication(appId);

  const { data: events, isLoading: eventsLoading } = useApplicationEvents(appId);
  const submitMutation = useSubmitApplication();

  const handleSubmit = async () => {
    try {
      await submitMutation.mutateAsync(appId);
      refetch();
    } catch {
      // Error shown inline
    }
  };

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in">
        <ApplicationDetailSkeleton />
      </div>
    );
  }

  // --- Error state ---
  if (isError) {
    return (
      <div className="animate-fade-in space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" /> Back to applications
        </button>
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  // --- Not found state ---
  if (!application) {
    return (
      <div className="animate-fade-in space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" /> Back to applications
        </button>
        <div className="flex flex-col items-center justify-center rounded-xl border bg-white p-12 shadow-sm">
          <AlertCircle className="mb-4 h-12 w-12 text-gray-300" />
          <h2 className="mb-2 text-lg font-semibold text-gray-900">Application not found</h2>
          <p className="mb-6 text-sm text-gray-500">This application may have been deleted or is no longer available.</p>
          <Link to="/applications" className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700">
            View All Applications
          </Link>
        </div>
      </div>
    );
  }

  // --- Populated state ---
  const canSubmit = application.allowed_transitions.includes("sent") || application.status === "draft";
  const submitError = submitMutation.isError ? getErrorMessage(submitMutation.error) : null;

  return (
    <div className="animate-fade-in space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to applications
      </button>

      {/* Header */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{application.job_title || "Untitled Application"}</h1>
            <p className="flex items-center gap-1.5 text-lg text-gray-500">
              <Building2 className="h-4 w-4" /> {application.company_name || "Unknown Company"}
            </p>
            <p className="mt-1 text-sm text-gray-400">
              Created {formatDate(application.created_at)}
              {application.sent_at && <> &middot; Sent {formatDate(application.sent_at)}</>}
            </p>
            <div className="mt-2">
              <StatusBadge status={application.status} size="md" />
            </div>
          </div>
          <div className="flex flex-col items-end gap-3">
            {application.match_score !== null && application.match_score !== undefined && (
              <div className="flex flex-col items-center">
                <span className="text-lg font-bold text-green-600">{Math.round(application.match_score)}%</span>
                <span className="text-xs text-gray-400">Match</span>
              </div>
            )}
            {canSubmit && (
              <button
                onClick={handleSubmit}
                disabled={submitMutation.isPending}
                className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50"
              >
                {submitMutation.isPending ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {submitMutation.isPending ? "Submitting..." : "Submit Application"}
              </button>
            )}
            {submitError && (
              <p className="text-xs text-red-600 max-w-60 text-right">{submitError}</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Timeline */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Application Timeline</h2>
          {eventsLoading ? (
            <div className="space-y-6">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex gap-4 animate-pulse">
                  <div className="h-8 w-8 shrink-0 rounded-full bg-gray-200" />
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="h-4 w-36 rounded bg-gray-200" />
                      <div className="h-3 w-16 rounded bg-gray-100" />
                    </div>
                    <div className="h-3 w-48 rounded bg-gray-100" />
                  </div>
                </div>
              ))}
            </div>
          ) : events && events.length > 0 ? (
            <TimelineView events={events} />
          ) : (
            <p className="py-8 text-center text-sm text-gray-400">No events recorded yet</p>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Application Package */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Application Package</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-700">Resume</span>
                </div>
                <span className={`text-sm font-medium ${application.resume_id ? "text-green-600" : "text-gray-400"}`}>
                  {application.resume_id ? "Attached" : "Not attached"}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-700">Cover Letter</span>
                </div>
                <span className={`text-sm font-medium ${application.cover_letter_id ? "text-green-600" : "text-gray-400"}`}>
                  {application.cover_letter_id ? "Generated" : "Not generated"}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-700">Email</span>
                </div>
                <span className={`text-sm font-medium ${application.email_id ? "text-green-600" : "text-gray-400"}`}>
                  {application.email_id ? "Prepared" : "Not prepared"}
                </span>
              </div>
            </div>
          </div>

          {/* Status Details */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Status Details</h2>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Current Status</dt>
                <dd>
                  <StatusBadge status={application.status} />
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Progress</dt>
                <dd className="flex items-center gap-2 font-medium text-gray-900">
                  <div className="h-1.5 w-20 rounded-full bg-gray-100">
                    <div
                      className="h-1.5 rounded-full bg-gradient-to-r from-primary-500 to-primary-600"
                      style={{ width: `${application.progress_percentage}%` }}
                    />
                  </div>
                  <span>{application.progress_percentage}%</span>
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Retry Count</dt>
                <dd className="font-medium text-gray-900">{application.retry_count}</dd>
              </div>
              {application.delivery_status && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Delivery Status</dt>
                  <dd className="flex items-center gap-1 font-medium">
                    {application.delivery_status === "delivered" ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                    ) : application.delivery_status === "failed" ? (
                      <XCircle className="h-3.5 w-3.5 text-red-500" />
                    ) : null}
                    {capitalize(application.delivery_status)}
                  </dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-gray-500">Updated</dt>
                <dd className="font-medium text-gray-900">{formatDate(application.updated_at)}</dd>
              </div>
            </dl>
          </div>

          {/* Notes */}
          {application.notes && (
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h2 className="mb-3 text-lg font-semibold text-gray-900">Notes</h2>
              <p className="whitespace-pre-line text-sm text-gray-600">{application.notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
