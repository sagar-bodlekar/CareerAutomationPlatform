import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Send,
  Eye,
  MessageCircle,
  CalendarCheck,
  Target,
  TrendingUp,
  Download,
  BarChart3,
  Bell,
  Inbox,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTrackingStats, useFunnel, useDailyTrends } from "../hooks/useTracking";
import StatsCard from "../components/tracking/StatsCard";
import ApplicationFunnel from "../components/tracking/ApplicationFunnel";
import DailyChart from "../components/tracking/DailyChart";
import { StatCardSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { exportTrackingData } from "../services/tracking";
import { getErrorMessage } from "../utils/errorHandler";

export default function TrackingPage() {
  const { user } = useAuth();
  const profileId = user?.id ?? 0;

  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
    error: statsErr,
    refetch: refetchStats,
  } = useTrackingStats(profileId);

  const {
    data: funnel,
    isLoading: funnelLoading,
  } = useFunnel(profileId);

  const {
    data: trends,
    isLoading: trendsLoading,
  } = useDailyTrends(profileId);

  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const handleExport = async (format: "csv" | "json") => {
    setExporting(true);
    setExportError(null);
    try {
      const result = await exportTrackingData(profileId, format);
      // Trigger download
      const blob = new Blob([result.content], { type: format === "csv" ? "text/csv" : "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename || `tracking-export.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setExportError(getErrorMessage(err));
    } finally {
      setExporting(false);
    }
  };

  const isLoading = statsLoading || funnelLoading || trendsLoading;
  const isPending = isLoading && !stats;

  // --- Loading state (initial) ---
  if (isPending) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="h-7 w-48 rounded bg-gray-200 animate-pulse" />
            <div className="mt-1 h-4 w-64 rounded bg-gray-100 animate-pulse" />
          </div>
          <div className="flex gap-2">
            <div className="h-9 w-24 rounded-lg bg-gray-200 animate-pulse" />
            <div className="h-9 w-28 rounded-lg bg-gray-200 animate-pulse" />
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <StatCardSkeleton key={i} />
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
            <div className="flex items-end gap-1" style={{ height: "160px" }}>
              {Array.from({ length: 30 }).map((_, i) => (
                <div key={i} className="flex flex-1 flex-col justify-end">
                  <div
                    className="w-full rounded-t bg-gray-200 animate-pulse"
                    style={{ height: `${20 + Math.random() * 60}%` }}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- Error state ---
  if (statsError) {
    return (
      <div className="animate-fade-in space-y-6">
        <ErrorFallback
          message={getErrorMessage(statsErr)}
          onRetry={() => refetchStats()}
        />
      </div>
    );
  }

  // --- Empty state ---
  if (stats && stats.total_applications === 0) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Tracking Dashboard</h1>
            <p className="text-gray-500">Monitor your application pipeline performance</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border bg-white p-16 shadow-sm">
          <Inbox className="mb-4 h-16 w-16 text-gray-300" />
          <h2 className="mb-2 text-lg font-semibold text-gray-900">No tracking data yet</h2>
          <p className="mb-6 max-w-sm text-center text-sm text-gray-500">
            Start applying to jobs to see your application tracking data, funnel metrics, and daily trends here.
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
  const openRate = stats?.total_sent ? Math.round((stats.total_opened / stats.total_sent) * 100) : 0;
  const replyRate = stats?.total_sent ? Math.round((stats.total_replied / stats.total_sent) * 100) : 0;
  const offerRate = stats?.total_sent ? Math.round((stats.total_offers / stats.total_sent) * 100) : 0;

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tracking Dashboard</h1>
          <p className="text-gray-500">Monitor your application pipeline performance</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/tracking/analytics"
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <BarChart3 className="h-4 w-4" />
            Analytics
          </Link>
          <Link
            to="/tracking/notifications"
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Bell className="h-4 w-4" />
            Notifications
          </Link>
          <button
            onClick={() => handleExport("csv")}
            disabled={exporting}
            className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            {exporting ? "Exporting..." : "Export"}
          </button>
        </div>
      </div>

      {exportError && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          Export failed: {exportError}
        </div>
      )}

      {/* Stats cards */}
      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatsCard
            icon={<Send className="h-6 w-6 text-white" />}
            label="Total Sent"
            value={stats.total_sent}
            subtext={`${stats.total_sent} of ${stats.total_applications} applications`}
            color="bg-blue-600"
          />
          <StatsCard
            icon={<Eye className="h-6 w-6 text-white" />}
            label="Opened"
            value={stats.total_opened}
            subtext={`${openRate}% open rate`}
            color="bg-emerald-600"
          />
          <StatsCard
            icon={<MessageCircle className="h-6 w-6 text-white" />}
            label="Replied"
            value={stats.total_replied}
            subtext={`${replyRate}% reply rate`}
            color="bg-green-600"
          />
          <StatsCard
            icon={<CalendarCheck className="h-6 w-6 text-white" />}
            label="Interviews"
            value={stats.total_interviews}
            subtext={stats.success_rate ? `${stats.success_rate}% success rate` : undefined}
            color="bg-lime-600"
          />
          <StatsCard
            icon={<Target className="h-6 w-6 text-white" />}
            label="Avg Match Score"
            value={stats.avg_match_score ? `${stats.avg_match_score}%` : "N/A"}
            subtext="Across all applications"
            color="bg-indigo-600"
          />
          <StatsCard
            icon={<TrendingUp className="h-6 w-6 text-white" />}
            label="Offers"
            value={stats.total_offers}
            subtext={`${offerRate}% conversion`}
            color="bg-amber-600"
          />
        </div>
      )}

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

        {/* Daily trends */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Daily Activity (30 days)</h2>
          {trends && trends.length > 0 ? (
            <>
              <DailyChart data={trends} />
              <div className="mt-4 flex items-center justify-center gap-6 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <span className="inline-block h-3 w-3 rounded bg-primary-400" /> Applications
                </span>
              </div>
            </>
          ) : (
            <p className="py-8 text-center text-sm text-gray-400">No activity data available</p>
          )}
        </div>
      </div>
    </div>
  );
}
