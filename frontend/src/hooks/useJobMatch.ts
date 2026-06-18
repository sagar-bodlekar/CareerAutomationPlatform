import { useQuery } from "@tanstack/react-query";
import { scoreMatch } from "../services/matches";

export function useJobMatch(profileId: number, jobId: number) {
  return useQuery({
    queryKey: ["jobMatch", profileId, jobId],
    queryFn: () => scoreMatch(profileId, jobId),
    enabled: !!profileId && !!jobId,
    retry: 1,
    staleTime: 5 * 60 * 1000, // Match scores are relatively stable
  });
}
