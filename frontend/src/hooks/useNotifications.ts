import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from "../services/notifications";

export function useNotifications(userId: string) {
  return useQuery({
    queryKey: ["notifications", userId],
    queryFn: () => getNotifications(userId),
    enabled: !!userId,
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}

export function useUnreadCount(userId: string) {
  return useQuery({
    queryKey: ["notifications", "unread", userId],
    queryFn: () => getUnreadCount(userId),
    enabled: !!userId,
    staleTime: 15_000,
    refetchInterval: 15_000,
  });
}

export function useMarkAsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, notificationId }: { userId: string; notificationId: number }) =>
      markAsRead(userId, notificationId),
    onMutate: async ({ userId, notificationId }) => {
      await qc.cancelQueries({ queryKey: ["notifications", userId] });

      // Snapshot previous unread count for rollback
      const previousUnread = qc.getQueryData<number>(["notifications", "unread", userId]);

      // Optimistic: mark notification as read in cache
      qc.setQueriesData<any[]>(
        { queryKey: ["notifications", userId] },
        (old) => {
          if (!old) return old;
          return old.map((n) =>
            n.id === notificationId ? { ...n, read: true } : n,
          );
        },
      );

      // Optimistic: decrement unread count
      qc.setQueryData<number>(
        ["notifications", "unread", userId],
        (old) => (old !== undefined ? Math.max(0, old - 1) : old),
      );

      return { previousUnread };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications", "unread"] });
    },
    onError: (_err, { userId }, context) => {
      // Rollback unread count
      if (context?.previousUnread !== undefined) {
        qc.setQueryData(["notifications", "unread", userId], context.previousUnread);
      }
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

export function useMarkAllAsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => markAllAsRead(userId),
    onMutate: async (userId) => {
      await qc.cancelQueries({ queryKey: ["notifications", userId] });

      const previousUnread = qc.getQueryData<number>(["notifications", "unread", userId]);

      // Optimistic: mark all as read
      qc.setQueriesData<any[]>(
        { queryKey: ["notifications", userId] },
        (old) => {
          if (!old) return old;
          return old.map((n) => ({ ...n, read: true }));
        },
      );

      // Optimistic: set unread count to 0
      qc.setQueryData<number>(["notifications", "unread", userId], 0);

      return { previousUnread };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications", "unread"] });
    },
    onError: (_err, userId, context) => {
      if (context?.previousUnread !== undefined) {
        qc.setQueryData(["notifications", "unread", userId], context.previousUnread);
      }
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
