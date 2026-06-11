import { useQuery } from "@tanstack/react-query";
import { searchJobs, getJob } from "../services/jobs";
import type { JobFilters } from "../services/jobs";

export type { JobFilters };

export function useJobs(filters: JobFilters = {}) {
  return useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => searchJobs(filters),
  });
}

export function useJob(id: number) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => getJob(id),
    enabled: !!id,
  });
}
