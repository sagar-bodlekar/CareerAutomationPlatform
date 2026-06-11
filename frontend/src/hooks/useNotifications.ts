import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from "../services/notifications";

export function useNotifications(userId: number) {
  return useQuery({
    queryKey: ["notifications", userId],
    queryFn: () => getNotifications(userId),
    enabled: !!userId,
    refetchInterval: 30_000, // Poll every 30s
  });
}

export function useUnreadCount(userId: number) {
  return useQuery({
    queryKey: ["notifications", "unread", userId],
    queryFn: () => getUnreadCount(userId),
    enabled: !!userId,
    refetchInterval: 15_000,
  });
}

export function useMarkAsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, notificationId }: { userId: number; notificationId: number }) =>
      markAsRead(userId, notificationId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

export function useMarkAllAsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => markAllAsRead(userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
