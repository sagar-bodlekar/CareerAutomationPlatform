import { Bell, CheckCheck } from "lucide-react";
import type { Notification } from "../../services/notifications";

interface Props {
  notifications: Notification[];
  onMarkRead?: (id: number) => void;
  onMarkAllRead?: () => void;
}

export default function NotificationList({ notifications, onMarkRead, onMarkAllRead }: Props) {
  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-400">
        <Bell className="mb-2 h-8 w-8" />
        <p className="text-sm">No notifications yet</p>
      </div>
    );
  }

  return (
    <div>
      {onMarkAllRead && (
        <div className="mb-3 flex justify-end">
          <button
            onClick={onMarkAllRead}
            className="flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-500"
          >
            <CheckCheck className="h-3 w-3" />
            Mark all as read
          </button>
        </div>
      )}

      <div className="space-y-2">
        {notifications.map((notif) => (
          <div
            key={notif.id}
            className={`rounded-lg border p-4 transition-colors ${
              notif.read ? "bg-white" : "bg-primary-50 border-primary-200"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <p className={`text-sm ${notif.read ? "text-gray-700" : "font-semibold text-gray-900"}`}>
                  {notif.title}
                </p>
                <p className="mt-0.5 text-xs text-gray-500">{notif.message}</p>
                <p className="mt-1 text-[10px] text-gray-400">
                  {new Date(notif.created_at).toLocaleDateString()}
                </p>
              </div>
              {!notif.read && onMarkRead && (
                <button
                  onClick={() => onMarkRead(notif.id)}
                  className="shrink-0 rounded p-1 text-gray-400 hover:bg-primary-100 hover:text-primary-600"
                  title="Mark as read"
                >
                  <CheckCheck className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
