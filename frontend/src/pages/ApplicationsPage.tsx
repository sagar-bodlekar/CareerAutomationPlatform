import { useState } from "react";
import { Link } from "react-router-dom";
import { Send, Clock } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useApplications } from "../hooks/useApplications";
import ApplicationCard from "../components/applications/ApplicationCard";
import { CardSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

const statusFilters = [
  { key: "all", label: "All" },
  { key: "draft", label: "Draft" },
  { key: "sent", label: "Sent" },
  { key: "delivered", label: "Delivered" },
  { key: "opened", label: "Opened" },
  { key: "replied", label: "Replied" },
  { key: "interview_scheduled", label: "Interview" },
  { key: "offer_received", label: "Offer" },
  { key: "rejected", label: "Rejected" },
];

export default function ApplicationsPage() {
  const { user } = useAuth();
  const profileId = user?.id ?? 0;

  const [filter, setFilter] = useState("all");

  const statusParam = filter === "all" ? undefined : filter;

  const {
    data,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useApplications(profileId, statusParam);

  const applications = data?.data ?? [];

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="text-gray-500">Track your job applications from draft to offer</p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {statusFilters.map((s) => (
          <button
            key={s.key}
            onClick={() => setFilter(s.key)}
            className={`whitespace-nowrap rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === s.key
                ? "bg-primary-600 text-white shadow-sm"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-3">
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
      {!isLoading && !isError && applications.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-16 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 mb-4">
            <Send className="h-6 w-6 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">No applications yet</h3>
          <p className="mt-1 text-sm text-gray-500 max-w-sm">
            {filter === "all"
              ? "Start your job search journey by finding matching opportunities."
              : `No applications with status "${statusFilters.find((s) => s.key === filter)?.label}".`}
          </p>
          {filter === "all" ? (              <Link
              to="/jobs"
              className="mt-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
            >
              Browse Jobs
            </Link>
          ) : (
            <button
              onClick={() => setFilter("all")}
              className="mt-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
            >
              View All Applications
            </button>
          )}
        </div>
      )}

      {/* Application cards */}
      {!isLoading && !isError && applications.length > 0 && (
        <div className="space-y-3">
          {applications.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))}

          {/* Refetch indicator */}
          {isFetching && (
            <div className="flex items-center justify-center gap-2 py-3 text-xs text-gray-400">
              <Clock className="h-3 w-3" />
              Updating...
            </div>
          )}
        </div>
      )}
    </div>
  );
}
