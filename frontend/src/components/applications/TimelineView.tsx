import { Clock, Send, CheckCircle2, Loader2, XCircle } from "lucide-react";
import type { ApplicationEvent } from "../../types";

interface Props {
  events: ApplicationEvent[];
}

const statusIcons: Record<string, React.ElementType> = {
  draft: Clock,
  sent: Send,
  delivered: CheckCircle2,
  opened: CheckCircle2,
  replied: CheckCircle2,
  interview_scheduled: Clock,
  offer_received: Loader2,
  rejected: XCircle,
  withdrawn: XCircle,
};

export default function TimelineView({ events }: Props) {
  if (events.length === 0) {
    return <p className="py-8 text-center text-sm text-gray-400">No events yet</p>;
  }

  return (
    <div className="relative">
      {events.map((event, i) => {
        const Icon = statusIcons[event.to_status] || Clock;
        const isLast = i === events.length - 1;

        return (
          <div key={event.id || i} className="relative flex gap-4 pb-8 last:pb-0">
            {!isLast && <div className="absolute left-4 top-8 h-full w-0.5 bg-gray-200" />}
            <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-600">
              <Icon className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {event.to_status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </p>
                  {event.description && <p className="text-xs text-gray-500">{event.description}</p>}
                </div>
                <span className="text-xs text-gray-400">{new Date(event.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
