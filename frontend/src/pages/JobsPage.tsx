import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, MapPin, Clock } from "lucide-react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useJobs } from "../hooks/useJobs";
import type { JobFilters } from "../hooks/useJobs";
import JobCard from "../components/jobs/JobCard";
import { CardSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage } from "../utils/errorHandler";

const PAGE_SIZE = 10;

export default function JobsPage() {
  useDocumentTitle("Browse Jobs");
  // Filter state
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [location, setLocation] = useState("");
  const [locationType, setLocationType] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [salaryMin, setSalaryMin] = useState("");
  const [salaryMax, setSalaryMax] = useState("");
  const [page, setPage] = useState(1);
  const [allJobs, setAllJobs] = useState<Array<Parameters<typeof JobCard>[0]["job"]>>([]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
      setPage(1);
      setAllJobs([]);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Build filters
  const filters: JobFilters = {
    ...(debouncedQuery && { query: debouncedQuery }),
    ...(location && { location }),
    ...(locationType && { location_type: locationType }),
    ...(employmentType && { employment_type: employmentType }),
    ...(salaryMin && { salary_min: parseInt(salaryMin, 10) * 1000 }),
    ...(salaryMax && { salary_max: parseInt(salaryMax, 10) * 1000 }),
    page,
    per_page: PAGE_SIZE,
  };

  const {
    data,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useJobs(filters);

  // Accumulate jobs across pages — guard against stale responses from rapid filter changes
  useEffect(() => {
    if (!data?.data) return;
    if (data.meta && data.meta.page !== page) return;
    if (page === 1) {
      setAllJobs(data.data);
    } else {
      setAllJobs((prev) => [...prev, ...data.data]);
    }
  }, [data, page]);

  const total = data?.meta?.total ?? 0;
  const hasMore = allJobs.length < total;

  function handleLoadMore() {
    if (!isFetching && hasMore) {
      setPage((p) => p + 1);
    }
  }

  function handleFiltersReset() {
    setQuery("");
    setDebouncedQuery("");
    setLocation("");
    setLocationType("");
    setEmploymentType("");
    setSalaryMin("");
    setSalaryMax("");
    setPage(1);
    setAllJobs([]);
  }

  const isInitialLoad = isLoading && page === 1;

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
        <p className="text-gray-500">Discover opportunities matched to your profile</p>
      </div>

      {/* Search + filters */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search jobs by title, company, or skills..."
            className="block w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <button
          onClick={() => setShowFilters((p) => !p)}
          className={`flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm transition-colors ${
            showFilters || location || locationType || employmentType || salaryMin || salaryMax
              ? "border-primary-300 bg-primary-50 text-primary-700"
              : "border-gray-300 text-gray-600 hover:bg-gray-50"
          }`}
        >
          <SlidersHorizontal className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
            <div>
              <label className="block text-xs font-medium text-gray-600">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => {
                  setLocation(e.target.value);
                  setPage(1);
                  setAllJobs([]);
                }}
                placeholder="City, state, or 'Remote'"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Location Type</label>
              <select
                value={locationType}
                onChange={(e) => setLocationType(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="">All</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Employment Type</label>
              <select
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="">All</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Min Salary</label>
              <div className="relative mt-1">
                <input
                  type="number"
                  value={salaryMin}
                  onChange={(e) => setSalaryMin(e.target.value)}
                  placeholder="e.g. 80"
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 pr-8 text-sm"
                />
                <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">k</span>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Max Salary</label>
              <div className="relative mt-1">
                <input
                  type="number"
                  value={salaryMax}
                  onChange={(e) => setSalaryMax(e.target.value)}
                  placeholder="e.g. 250"
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 pr-8 text-sm"
                />
                <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">k</span>
              </div>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between border-t pt-3">
            <button
              onClick={handleFiltersReset}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              Reset filters
            </button>
            <button
              onClick={() => setShowFilters(false)}
              className="rounded-lg bg-primary-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      )}

      {/* Job list */}
      <div className="space-y-3">
        {/* Initial loading state */}
        {isInitialLoad && (
          <>
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </>
        )}

        {/* Error state */}
        {!isInitialLoad && isError && (
          <ErrorFallback
            message={getErrorMessage(error)}
            onRetry={() => refetch()}
          />
        )}

        {/* Empty state */}
        {!isInitialLoad && !isError && allJobs.length === 0 && !isFetching && (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 mb-4">
              <MapPin className="h-6 w-6 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">No jobs found</h3>
            <p className="mt-1 text-sm text-gray-500 max-w-sm">
              {debouncedQuery || location || locationType || employmentType || salaryMin || salaryMax
                ? "No jobs match your filters. Try broadening your search."
                : "There are no jobs available right now. Check back later."}
            </p>
            {(debouncedQuery || location || locationType || employmentType || salaryMin || salaryMax) && (
              <button
                onClick={handleFiltersReset}
                className="mt-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
              >
                Reset Filters
              </button>
            )}
          </div>
        )}

        {/* Job cards */}
        {allJobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            logo={job.company_name?.charAt(0) ?? "?"}
          />
        ))}

        {/* Loading more indicator */}
        {isFetching && !isInitialLoad && (
          <div className="flex justify-center py-4">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          </div>
        )}

        {/* Load more */}
        {!isInitialLoad && !isError && hasMore && !isFetching && (
          <div className="flex justify-center pt-2">
            <button
              onClick={handleLoadMore}
              className="flex items-center gap-2 rounded-lg border border-gray-300 px-6 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Clock className="h-4 w-4" />
              Load More ({allJobs.length} of {total})
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
