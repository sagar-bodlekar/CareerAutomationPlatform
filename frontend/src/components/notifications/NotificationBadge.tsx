import { Bell } from "lucide-react";

interface Props {
  count: number;
  onClick?: () => void;
}

export default function NotificationBadge({ count, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="relative rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
    >
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-danger-500 text-[10px] font-bold text-white">
          {count > 99 ? "99+" : count}
        </span>
      )}
    </button>
  );
}
