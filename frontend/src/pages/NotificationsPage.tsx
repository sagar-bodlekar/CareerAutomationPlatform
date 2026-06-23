import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Bell, BellOff } from "lucide-react";
import NotificationList from "../components/notifications/NotificationList";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useAuth } from "../context/AuthContext";
import { useNotifications, useUnreadCount, useMarkAsRead, useMarkAllAsRead } from "../hooks/useNotifications";
import { ActivitySkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

export default function NotificationsPage() {
  useDocumentTitle("Notifications");
  const { user } = useAuth();
  const userId = user?.id ?? "";

  const [filter, setFilter] = useState<"all" | "unread">("all");

  const {
    data: notifications,
    isLoading,
    isError,
    error,
    refetch,
  } = useNotifications(userId);

  const { data: unreadCount } = useUnreadCount(userId);

  const markAsReadMutation = useMarkAsRead();
  const markAllAsReadMutation = useMarkAllAsRead();

  const handleMarkRead = (id: number) => {
    markAsReadMutation.mutate({ userId, notificationId: id });
  };

  const handleMarkAllRead = () => {
    markAllAsReadMutation.mutate(userId);
  };

  const filtered = filter === "unread"
    ? (notifications ?? []).filter((n) => !n.read)
    : (notifications ?? []);

  const displayUnreadCount = unreadCount ?? notifications?.filter((n) => !n.read).length ?? 0;

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-9 w-9 rounded-lg bg-gray-200 animate-pulse" />
            <div className="space-y-1">
              <div className="h-7 w-40 rounded bg-gray-200 animate-pulse" />
              <div className="h-4 w-32 rounded bg-gray-100 animate-pulse" />
            </div>
          </div>
          <div className="h-9 w-36 rounded-lg bg-gray-200 animate-pulse" />
        </div>
        <div className="flex gap-2">
          <div className="h-8 w-16 rounded-full bg-gray-200 animate-pulse" />
          <div className="h-8 w-20 rounded-full bg-gray-200 animate-pulse" />
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <ActivitySkeleton />
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
  if (notifications && notifications.length === 0) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center gap-4">
          <Link to="/tracking" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
              <Bell className="h-6 w-6 text-primary-500" /> Notifications
            </h1>
            <p className="text-gray-500">No notifications yet</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border bg-white p-16 shadow-sm">
          <BellOff className="mb-4 h-16 w-16 text-gray-300" />
          <h2 className="mb-2 text-lg font-semibold text-gray-900">All caught up</h2>
          <p className="max-w-sm text-center text-sm text-gray-500">
            You don't have any notifications yet. Notifications about your applications, job matches, and updates will appear here.
          </p>
        </div>
      </div>
    );
  }

  // --- Populated state ---
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/tracking" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
              <Bell className="h-6 w-6 text-primary-500" /> Notifications
            </h1>
            <p className="text-gray-500">
              {displayUnreadCount} unread notification{displayUnreadCount !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
        {displayUnreadCount > 0 && (
          <button
            onClick={handleMarkAllRead}
            disabled={markAllAsReadMutation.isPending}
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            {markAllAsReadMutation.isPending ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
            ) : (
              <BellOff className="h-4 w-4" />
            )}
            Mark all read
          </button>
        )}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {(["all", "unread"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === f ? "bg-primary-600 text-white shadow-sm" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {f === "all" ? "All" : "Unread"}
            {displayUnreadCount > 0 && (
              <span className="ml-1.5 inline-flex items-center justify-center rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">
                {displayUnreadCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Notification list */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <NotificationList
          notifications={filtered}
          onMarkRead={handleMarkRead}
        />
      </div>
    </div>
  );
}
