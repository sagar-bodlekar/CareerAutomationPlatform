import { getById } from "./api";

export interface TrackingStats {
  total_applications: number;
  total_sent: number;
  total_delivered: number;
  total_opened: number;
  total_replied: number;
  total_interviews: number;
  total_offers: number;
  total_rejected: number;
  avg_match_score?: number;
  avg_response_time_hours?: number;
  success_rate?: number;
}

export interface FunnelItem {
  status: string;
  label: string;
  count: number;
  percentage: number;
}

export interface DailyTrend {
  date: string;
  count: number;
  sent_count: number;
  interview_count: number;
  offer_count: number;
}

export interface AnalyticsData {
  total_applications: number;
  funnel: FunnelItem[];
  daily_trends: DailyTrend[];
  source_breakdown: Array<{ source: string; count: number; interview_count: number; success_rate?: number }>;
  avg_response_time?: number;
  response_rate?: number;
}

export async function getTrackingStats(profileId: number): Promise<TrackingStats> {
  return getById(`/tracking/stats?profile_id=${profileId}`);
}

export async function getAnalytics(profileId: number): Promise<AnalyticsData> {
  return getById(`/tracking/analytics?profile_id=${profileId}`);
}

export async function getFunnel(profileId: number): Promise<FunnelItem[]> {
  const { default: api } = await import("./api");
  const { data } = await api.get(`/tracking/funnel?profile_id=${profileId}`);
  return data.data as FunnelItem[];
}

export async function getDailyTrends(profileId: number, days = 30): Promise<DailyTrend[]> {
  const { default: api } = await import("./api");
  const { data } = await api.get(`/tracking/trends?profile_id=${profileId}&days=${days}`);
  return data.data as DailyTrend[];
}

export async function exportTrackingData(profileId: number, format: "csv" | "json" = "json") {
  const { default: api } = await import("./api");
  const { data } = await api.post(`/tracking/export?profile_id=${profileId}&format=${format}`);
  return data.data as { format: string; content: string; filename: string };
}
