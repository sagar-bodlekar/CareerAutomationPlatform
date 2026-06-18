import { Link } from "react-router-dom";
import { ArrowLeft, Globe, Clock, Percent, BarChart3, Inbox } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useAnalytics } from "../hooks/useTracking";
import SourceBreakdown from "../components/tracking/SourceBreakdown";
import ApplicationFunnel from "../components/tracking/ApplicationFunnel";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

function MetricSkeleton() {
  return (
    <div className="animate-pulse rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gray-200" />
        <div className="space-y-2">
          <div className="h-3 w-24 rounded bg-gray-200" />
          <div className="h-5 w-12 rounded bg-gray-200" />
        </div>
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const { user } = useAuth();
  const profileId = user?.id ?? 0;

  const {
    data: analytics,
    isLoading,
    isError,
    error,
    refetch,
  } = useAnalytics(profileId);

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center gap-4">
          <div className="h-9 w-9 rounded-lg bg-gray-200 animate-pulse" />
          <div className="space-y-1">
            <div className="h-7 w-32 rounded bg-gray-200 animate-pulse" />
            <div className="h-4 w-56 rounded bg-gray-100 animate-pulse" />
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <MetricSkeleton key={i} />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="mb-4 h-5 w-40 rounded bg-gray-200 animate-pulse" />
            <div className="space-y-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between">
                    <div className="h-4 w-20 rounded bg-gray-200 animate-pulse" />
                    <div className="h-4 w-24 rounded bg-gray-100 animate-pulse" />
                  </div>
                  <div className="h-2.5 rounded-full bg-gray-100">
                    <div className="h-2.5 w-3/4 rounded-full bg-gray-200 animate-pulse" />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="mb-4 h-5 w-40 rounded bg-gray-200 animate-pulse" />
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3 animate-pulse">
                  <div className="space-y-1">
                    <div className="h-4 w-28 rounded bg-gray-200" />
                    <div className="h-3 w-20 rounded bg-gray-100" />
                  </div>
                  <div className="space-y-1 text-right">
                    <div className="h-4 w-16 rounded bg-gray-200" />
                    <div className="h-3 w-12 rounded bg-gray-100" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- Error state ---
  if (isError) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/tracking" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
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

  // --- Empty state ---
  if (!analytics || analytics.total_applications === 0) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/tracking" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-500">Detailed breakdown of your application performance</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border bg-white p-16 shadow-sm">
          <Inbox className="mb-4 h-16 w-16 text-gray-300" />
          <h2 className="mb-2 text-lg font-semibold text-gray-900">No analytics data yet</h2>
          <p className="mb-6 max-w-sm text-center text-sm text-gray-500">
            Submit applications to see detailed analytics including response rates, funnel metrics, and source performance.
          </p>
          <Link
            to="/jobs"
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700"
          >
            Browse Jobs
          </Link>
        </div>
      </div>
    );
  }

  // --- Populated state ---
  const { funnel, source_breakdown, response_rate, avg_response_time } = analytics;
  const interviewRate = analytics.total_applications > 0
    ? Math.round((funnel.find((f) => f.status === "interview_scheduled")?.count ?? 0) / analytics.total_applications * 100)
    : 0;

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/tracking" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500">Detailed breakdown of your application performance</p>
        </div>
      </div>

      {/* Key metrics */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
              <Percent className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Response Rate</p>
              <p className="text-xl font-bold text-gray-900">
                {response_rate !== undefined ? `${Math.round(response_rate)}%` : "N/A"}
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
              <Clock className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg Response Time</p>
              <p className="text-xl font-bold text-gray-900">
                {avg_response_time !== undefined
                  ? `${avg_response_time < 24 ? `${avg_response_time.toFixed(1)}h` : `${(avg_response_time / 24).toFixed(1)}d`}`
                  : "N/A"}
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100">
              <BarChart3 className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Interview Rate</p>
              <p className="text-xl font-bold text-gray-900">{interviewRate}%</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Funnel */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Application Funnel</h2>
          {funnel && funnel.length > 0 ? (
            <ApplicationFunnel data={funnel} />
          ) : (
            <p className="py-8 text-center text-sm text-gray-400">No funnel data available</p>
          )}
        </div>

        {/* Source breakdown */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <Globe className="h-5 w-5 text-gray-500" /> Source Performance
          </h2>
          {source_breakdown && source_breakdown.length > 0 ? (
            <SourceBreakdown data={source_breakdown} />
          ) : (
            <p className="py-8 text-center text-sm text-gray-400">No source data available</p>
          )}
        </div>
      </div>
    </div>
  );
}
