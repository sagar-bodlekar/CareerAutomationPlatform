import type { FunnelItem } from "../../services/tracking";

interface Props {
  data: FunnelItem[];
}

const statusColors: Record<string, string> = {
  draft: "bg-gray-400",
  sent: "bg-cyan-500",
  delivered: "bg-teal-500",
  opened: "bg-emerald-500",
  replied: "bg-green-500",
  interview_scheduled: "bg-lime-500",
  offer_received: "bg-amber-500",
  rejected: "bg-red-500",
  withdrawn: "bg-gray-300",
};

export default function ApplicationFunnel({ data }: Props) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);

  return (
    <div className="space-y-3">
      {data.map((item) => (
        <div key={item.status} className="group">
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="font-medium text-gray-700">{item.label}</span>
            <span className="text-gray-500">
              {item.count} ({item.percentage}%)
            </span>
          </div>
          <div className="h-2.5 rounded-full bg-gray-100">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 group-hover:opacity-80 ${
                statusColors[item.status] || "bg-gray-400"
              }`}
              style={{ width: `${(item.count / maxCount) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
