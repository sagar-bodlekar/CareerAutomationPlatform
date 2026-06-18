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

export function ProfileSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      {/* Personal info card skeleton */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="h-16 w-16 rounded-2xl bg-gray-200" />
          <div className="flex-1 space-y-3">
            <div className="h-5 w-48 rounded bg-gray-200" />
            <div className="h-4 w-32 rounded bg-gray-100" />
            <div className="flex gap-4">
              <div className="h-3 w-40 rounded bg-gray-100" />
              <div className="h-3 w-36 rounded bg-gray-100" />
            </div>
          </div>
        </div>
      </div>

      {/* Skills + Experience grid skeletons */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="h-5 w-20 rounded bg-gray-200 mb-4" />
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-4 w-24 rounded bg-gray-200" />
                  <div className="h-5 w-16 rounded-full bg-gray-100" />
                </div>
                <div className="h-5 w-14 rounded-full bg-gray-100" />
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="h-5 w-24 rounded bg-gray-200 mb-4" />
          <div className="space-y-4">
            {Array.from({ length: 2 }).map((_, i) => (
              <div key={i} className="border-l-2 border-gray-200 pl-4">
                <div className="h-4 w-40 rounded bg-gray-200" />
                <div className="h-3 w-28 rounded bg-gray-100 mt-1" />
                <div className="h-3 w-20 rounded bg-gray-100 mt-1" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function JobDetailSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      {/* Back button */}
      <div className="h-4 w-24 rounded bg-gray-200" />

      {/* Header card */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="h-16 w-16 shrink-0 rounded-2xl bg-gray-200" />
            <div className="space-y-3">
              <div className="h-6 w-72 rounded bg-gray-200" />
              <div className="h-4 w-40 rounded bg-gray-100" />
              <div className="flex gap-4">
                <div className="h-4 w-32 rounded bg-gray-100" />
                <div className="h-4 w-28 rounded bg-gray-100" />
                <div className="h-4 w-24 rounded bg-gray-100" />
              </div>
            </div>
          </div>
          <div className="h-16 w-16 rounded-full bg-gray-100" />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="h-5 w-28 rounded bg-gray-200 mb-3" />
            <div className="space-y-2">
              <div className="h-4 w-full rounded bg-gray-100" />
              <div className="h-4 w-5/6 rounded bg-gray-100" />
              <div className="h-4 w-4/6 rounded bg-gray-100" />
            </div>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="h-5 w-28 rounded bg-gray-200 mb-3" />
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-4 w-4/6 rounded bg-gray-100" />
              ))}
            </div>
          </div>
        </div>
        <div className="space-y-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="h-5 w-20 rounded bg-gray-200 mb-3" />
            <div className="space-y-3">
              <div className="h-10 w-full rounded-lg bg-gray-200" />
              <div className="h-10 w-full rounded-lg bg-gray-100" />
            </div>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="h-5 w-28 rounded bg-gray-200 mb-3" />
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-6 w-16 rounded-full bg-gray-100" />
              ))}
            </div>
          </div>
        </div>
      </div>
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
