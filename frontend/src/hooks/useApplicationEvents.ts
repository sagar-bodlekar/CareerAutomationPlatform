import { useQuery } from "@tanstack/react-query";
import { getApplicationEvents } from "../services/applications";

export function useApplicationEvents(id: number) {
  return useQuery({
    queryKey: ["applicationEvents", id],
    queryFn: () => getApplicationEvents(id),
    enabled: !!id,
  });
}
