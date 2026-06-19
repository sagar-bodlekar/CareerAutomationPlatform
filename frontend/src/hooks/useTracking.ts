import { useQuery } from "@tanstack/react-query";
import { getTrackingStats, getAnalytics, getDailyTrends, getFunnel } from "../services/tracking";

export function useTrackingStats(profileId: string) {
  return useQuery({
    queryKey: ["tracking", "stats", profileId],
    queryFn: () => getTrackingStats(profileId),
    enabled: !!profileId,
    staleTime: 60_000,         // 1 min
    refetchInterval: 120_000,  // Poll every 2 min
  });
}

export function useAnalytics(profileId: string) {
  return useQuery({
    queryKey: ["tracking", "analytics", profileId],
    queryFn: () => getAnalytics(profileId),
    enabled: !!profileId,
    staleTime: 2 * 60 * 1000,  // 2 min — analytics are cached
  });
}

export function useFunnel(profileId: string) {
  return useQuery({
    queryKey: ["tracking", "funnel", profileId],
    queryFn: () => getFunnel(profileId),
    enabled: !!profileId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useDailyTrends(profileId: string, days = 30) {
  return useQuery({
    queryKey: ["tracking", "trends", profileId, days],
    queryFn: () => getDailyTrends(profileId, days),
    enabled: !!profileId,
    staleTime: 2 * 60 * 1000,
  });
}
