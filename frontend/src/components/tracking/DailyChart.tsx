import type { DailyTrend } from "../../services/tracking";

interface Props {
  data: DailyTrend[];
}

export default function DailyChart({ data }: Props) {
  const maxCount = Math.max(...data.map((d) => Math.max(d.count, d.sent_count, 1)));

  return (
    <div className="relative">
      <div className="flex items-end gap-1" style={{ height: "160px" }}>
        {data.map((day, i) => {
          const height = (day.count / maxCount) * 100;
          return (
            <div
              key={i}
              className="group relative flex flex-1 flex-col justify-end"
              title={`${day.date}: ${day.count} total, ${day.sent_count} sent`}
            >
              <div className="flex flex-col items-center gap-0.5">
                <div
                  className="w-full rounded-t bg-primary-400 transition-all hover:bg-primary-500"
                  style={{ height: `${Math.max(height, 2)}%` }}
                />
              </div>
              {data.length <= 31 && i % 5 === 0 && (
                <span className="mt-1 text-[10px] text-gray-400 -rotate-45 origin-left">
                  {day.date.slice(5)}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
