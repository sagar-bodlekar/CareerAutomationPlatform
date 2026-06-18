import { useQuery } from "@tanstack/react-query";
import { getRecentActivity } from "../services/tracking";

export function useRecentActivity(profileId: number, limit = 10) {
  return useQuery({
    queryKey: ["tracking", "activity", profileId, limit],
    queryFn: () => getRecentActivity(profileId, limit),
    enabled: !!profileId,
    refetchInterval: 60_000, // Refresh every minute
  });
}
