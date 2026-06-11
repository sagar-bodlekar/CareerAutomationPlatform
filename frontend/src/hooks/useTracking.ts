import { useQuery } from "@tanstack/react-query";
import { getTrackingStats, getAnalytics, getDailyTrends, getFunnel } from "../services/tracking";

export function useTrackingStats(profileId: number) {
  return useQuery({
    queryKey: ["tracking", "stats", profileId],
    queryFn: () => getTrackingStats(profileId),
    enabled: !!profileId,
  });
}

export function useAnalytics(profileId: number) {
  return useQuery({
    queryKey: ["tracking", "analytics", profileId],
    queryFn: () => getAnalytics(profileId),
    enabled: !!profileId,
  });
}

export function useFunnel(profileId: number) {
  return useQuery({
    queryKey: ["tracking", "funnel", profileId],
    queryFn: () => getFunnel(profileId),
    enabled: !!profileId,
  });
}

export function useDailyTrends(profileId: number, days = 30) {
  return useQuery({
    queryKey: ["tracking", "trends", profileId, days],
    queryFn: () => getDailyTrends(profileId, days),
    enabled: !!profileId,
  });
}
