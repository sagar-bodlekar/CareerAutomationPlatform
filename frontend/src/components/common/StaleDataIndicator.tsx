import { useEffect, useState } from "react";
import { Clock } from "lucide-react";
import { formatRelativeTime } from "../../utils/formatters";

interface StaleDataIndicatorProps {
  /** ISO timestamp of when data was last fetched */
  lastFetchedAt?: string | Date;
  /** How many ms before the indicator turns yellow (stale) */
  staleAfter?: number;
  /** How many ms before the indicator turns red (very stale) */
  veryStaleAfter?: number;
  /** Additional class names */
  className?: string;
}

export function StaleDataIndicator({
  lastFetchedAt,
  staleAfter = 60_000,
  veryStaleAfter = 300_000,
  className = "",
}: StaleDataIndicatorProps) {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    if (!lastFetchedAt) return;
    const tick = () => setNow(Date.now());
    const id = setInterval(tick, 30_000); // Update every 30s
    return () => clearInterval(id);
  }, [lastFetchedAt]);

  if (!lastFetchedAt) return null;

  const lastFetch = new Date(lastFetchedAt).getTime();
  const age = now - lastFetch;

  let color = "text-gray-400";
  let label = "Up to date";

  if (age > veryStaleAfter) {
    color = "text-amber-500";
    label = "Data may be stale";
  } else if (age > staleAfter) {
    color = "text-gray-400";
    label = "";
  }

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs ${color} ${className}`}
      title={`Last updated ${formatRelativeTime(lastFetchedAt)}`}
    >
      <Clock className="h-3 w-3" />
      <span>{formatRelativeTime(lastFetchedAt)}</span>
      {label && <span className="hidden sm:inline">· {label}</span>}
    </span>
  );
}
