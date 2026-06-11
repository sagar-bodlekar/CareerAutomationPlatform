import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Bell, CheckCheck } from "lucide-react";
import NotificationList from "../components/notifications/NotificationList";

const mockNotifications = [
  { id: 1, type: "application_status", title: "Application Sent", message: "Your application for Senior Software Engineer at Tech Corp has been sent.", data: {}, read: false, created_at: new Date().toISOString() },
  { id: 2, type: "application_status", title: "Application Delivered", message: "Your application for Backend Developer at DataFlow has been delivered.", data: {}, read: false, created_at: new Date(Date.now() - 86400000).toISOString() },
  { id: 3, type: "job_match", title: "New Job Match", message: "New match: ML Engineer at AI Labs (85% match)", data: {}, read: true, created_at: new Date(Date.now() - 172800000).toISOString() },
  { id: 4, type: "application_status", title: "Interview Scheduled", message: "Interview scheduled for Frontend Engineer at Startup Inc.", data: {}, read: true, created_at: new Date(Date.now() - 259200000).toISOString() },
  { id: 5, type: "application_status", title: "Offer Received", message: "Congratulations! You received an offer from Tech Corp.", data: {}, read: true, created_at: new Date(Date.now() - 345600000).toISOString() },
];

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState(mockNotifications);
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const filtered = filter === "unread" ? notifications.filter((n) => !n.read) : notifications;

  const handleMarkRead = (id: number) => {
    setNotifications(notifications.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  const handleMarkAllRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, read: true })));
  };

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
              {notifications.filter((n) => !n.read).length} unread notifications
            </p>
          </div>
        </div>
        <button
          onClick={handleMarkAllRead}
          className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <CheckCheck className="h-4 w-4" />
          Mark all read
        </button>
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
            {f === "unread" && notifications.filter((n) => !n.read).length > 0 && (
              <span className="ml-1.5 inline-flex items-center justify-center rounded-full bg-danger-500 px-1.5 py-0.5 text-xs text-white">
                {notifications.filter((n) => !n.read).length}
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
          onMarkAllRead={handleMarkAllRead}
        />
      </div>
    </div>
  );
}
