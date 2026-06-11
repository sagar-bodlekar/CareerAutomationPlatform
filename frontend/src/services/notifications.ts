import api from "./api";

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  data?: Record<string, unknown>;
  read: boolean;
  created_at: string;
}

export async function getNotifications(userId: number, limit = 20, unreadOnly = false): Promise<Notification[]> {
  const { data } = await api.get("/notifications", { params: { user_id: userId, limit, unread_only: unreadOnly } });
  return data.data as Notification[];
}

export async function getUnreadCount(userId: number): Promise<number> {
  const { data } = await api.get(`/notifications/unread/count?user_id=${userId}`);
  return (data.data as { count: number }).count;
}

export async function markAsRead(userId: number, notificationId: number): Promise<boolean> {
  const { data } = await api.post(`/notifications/${notificationId}/read?user_id=${userId}`);
  return (data.data as { success: boolean }).success;
}

export async function markAllAsRead(userId: number): Promise<number> {
  const { data } = await api.post(`/notifications/read-all?user_id=${userId}`);
  return (data.data as { marked: number }).marked;
}
