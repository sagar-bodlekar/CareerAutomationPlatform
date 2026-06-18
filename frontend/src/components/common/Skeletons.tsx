export function StatCardSkeleton() {
  return (
    <div className="animate-pulse rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-xl bg-gray-200" />
        <div className="flex-1 space-y-2">
          <div className="h-3 w-20 rounded bg-gray-200" />
          <div className="h-6 w-16 rounded bg-gray-200" />
          <div className="h-3 w-24 rounded bg-gray-100" />
        </div>
      </div>
    </div>
  );
}

export function ActivitySkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-start gap-3 animate-pulse">
          <div className="h-8 w-8 shrink-0 rounded-lg bg-gray-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-3/4 rounded bg-gray-200" />
            <div className="h-3 w-16 rounded bg-gray-100" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="animate-pulse rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-start gap-4">
        <div className="h-12 w-12 shrink-0 rounded-xl bg-gray-200" />
        <div className="flex-1 space-y-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 rounded bg-gray-200" />
              <div className="h-3 w-1/3 rounded bg-gray-100" />
            </div>
            <div className="h-5 w-12 rounded-full bg-gray-200" />
          </div>
          <div className="flex gap-3">
            <div className="h-3 w-24 rounded bg-gray-100" />
            <div className="h-3 w-16 rounded bg-gray-100" />
            <div className="h-3 w-20 rounded bg-gray-100" />
          </div>
          <div className="flex gap-1.5">
            <div className="h-5 w-16 rounded-full bg-gray-100" />
            <div className="h-5 w-20 rounded-full bg-gray-100" />
            <div className="h-5 w-14 rounded-full bg-gray-100" />
          </div>
        </div>
      </div>
    </div>
  );
}
