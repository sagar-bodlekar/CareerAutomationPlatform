import { Link } from "react-router-dom";
import {
  Briefcase,
  FileText,
  Send,
  TrendingUp,
  Users,
  Clock,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTrackingStats } from "../hooks/useTracking";
import { useRecentActivity } from "../hooks/useRecentActivity";
import { useProfile } from "../hooks/useProfile";
import { StatCardSkeleton, ActivitySkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";
import { formatRelativeTime } from "../utils/formatters";

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  trend?: string;
  color: string;
}

function StatCard({ icon: Icon, label, value, trend, color }: StatCardProps) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center gap-4">
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && <p className="text-xs text-green-600">{trend}</p>}
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();

  // The user's id from auth context doubles as profile_id for dashboard queries
  const profileId = user?.id ?? 0;

  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
    error: statsErr,
    refetch: refetchStats,
  } = useTrackingStats(profileId);

  const {
    data: activity,
    isLoading: activityLoading,
    isError: activityError,
    error: activityErr,
    refetch: refetchActivity,
  } = useRecentActivity(profileId);

  const { data: profile } = useProfile(profileId);

  const isLoading = statsLoading || activityLoading;
  const hasError = statsError || activityError;

  // Welcome message
  const displayName = profile?.personal_info?.full_name || user?.email?.split("@")[0] || "";

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome{displayName ? `, ${displayName}` : ""}
        </h1>
        <p className="mt-1 text-gray-500">Here's your career activity overview</p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : hasError ? (
          <div className="col-span-full">
            <ErrorFallback
              message={getErrorMessage(statsErr ?? activityErr)}
              onRetry={() => { refetchStats(); refetchActivity(); }}
            />
          </div>
        ) : (
          <>
            <StatCard
              icon={Briefcase}
              label="Active Applications"
              value={stats?.total_applications ?? 0}
              trend={stats && stats.total_applications > 0 ? `${stats.total_applications} in progress` : undefined}
              color="bg-blue-600"
            />
            <StatCard
              icon={FileText}
              label="Applications Sent"
              value={stats?.total_sent ?? 0}
              trend={stats?.success_rate ? `${stats.success_rate}% delivery rate` : undefined}
              color="bg-indigo-600"
            />
            <StatCard
              icon={Send}
              label="Delivered"
              value={stats?.total_delivered ?? 0}
              trend={stats && stats.total_opened ? `${Math.round((stats.total_opened / stats.total_delivered) * 100)}% open rate` : undefined}
              color="bg-cyan-600"
            />
            <StatCard
              icon={Users}
              label="Replies"
              value={stats?.total_replied ?? 0}
              trend={stats ? `${stats.total_interviews ?? 0} interviews` : undefined}
              color="bg-green-600"
            />
          </>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Quick actions */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Actions</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <Link
              to="/jobs"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700"
            >
              <Briefcase className="h-5 w-5" />
              Browse Jobs
            </Link>
            <Link
              to="/resumes"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-700"
            >
              <FileText className="h-5 w-5" />
              Manage Resumes
            </Link>
            <Link
              to="/applications"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-cyan-50 hover:border-cyan-200 hover:text-cyan-700"
            >
              <Send className="h-5 w-5" />
              View Applications
            </Link>
            <Link
              to="/profile/edit"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-amber-50 hover:border-amber-200 hover:text-amber-700"
            >
              <Users className="h-5 w-5" />
              Edit Profile
            </Link>
          </div>
        </div>

        {/* Recent activity */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Recent Activity</h2>
          {activityLoading ? (
            <ActivitySkeleton />
          ) : activityError ? (
            <ErrorFallback
              message={getErrorMessage(activityErr)}
              onRetry={() => refetchActivity()}
              compact
            />
          ) : !activity || activity.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 mb-3">
                <Clock className="h-5 w-5 text-gray-400" />
              </div>
              <p className="text-sm font-medium text-gray-900">No activity yet</p>
              <p className="mt-1 text-xs text-gray-500">
                Start by browsing jobs and submitting your first application
              </p>
              <Link
                to="/jobs"
                className="mt-3 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                Browse Jobs
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {activity.map((item) => (
                <div key={item.id} className="flex items-start gap-3">
                  <div
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                      item.type === "interview"
                        ? "bg-amber-500"
                        : item.type === "offer"
                          ? "bg-green-500"
                          : item.type === "resume"
                            ? "bg-indigo-500"
                            : "bg-blue-500"
                    }`}
                  >
                    {item.type === "interview" || item.type === "offer" ? (
                      <TrendingUp className="h-4 w-4 text-white" />
                    ) : (
                      <Briefcase className="h-4 w-4 text-white" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700">{item.description}</p>
                    <p className="text-xs text-gray-400">{formatRelativeTime(item.timestamp)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
