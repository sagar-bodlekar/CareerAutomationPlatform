import { useQuery } from "@tanstack/react-query";
import { searchJobs, getJob } from "../services/jobs";
import type { JobFilters } from "../services/jobs";

export type { JobFilters };

export function useJobs(filters: JobFilters = {}) {
  return useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => searchJobs(filters),
    staleTime: 2 * 60 * 1000, // 2 min — moderate freshness
  });
}

export function useJob(id: number) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => getJob(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 min — job details relatively stable
  });
}
