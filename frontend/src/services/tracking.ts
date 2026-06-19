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

export async function getTrackingStats(profileId: string): Promise<TrackingStats> {
  return getById(`/tracking/stats?profile_id=${profileId}`);
}

export async function getAnalytics(profileId: string): Promise<AnalyticsData> {
  return getById(`/tracking/analytics?profile_id=${profileId}`);
}

export async function getFunnel(profileId: string): Promise<FunnelItem[]> {
  const { default: api } = await import("./api");
  const { data } = await api.get(`/tracking/funnel?profile_id=${profileId}`);
  return data.data as FunnelItem[];
}

export async function getDailyTrends(profileId: string, days = 30): Promise<DailyTrend[]> {
  const { default: api } = await import("./api");
  const { data } = await api.get(`/tracking/trends?profile_id=${profileId}&days=${days}`);
  return data.data as DailyTrend[];
}

export async function exportTrackingData(profileId: string, format: "csv" | "json" = "json") {
  const { default: api } = await import("./api");
  const { data } = await api.post(`/tracking/export?profile_id=${profileId}&format=${format}`);
  return data.data as { format: string; content: string; filename: string };
}

export interface ActivityItem {
  id: number;
  type: "application" | "resume" | "match" | "interview" | "offer";
  title: string;
  description: string;
  timestamp: string;
  application_id?: number;
  job_id?: number;
}

export async function getRecentActivity(profileId: string, limit = 10): Promise<ActivityItem[]> {
  const { default: api } = await import("./api");
  const response = await api.get(`/tracking/applications?profile_id=${profileId}&per_page=${limit}`);
  const raw = response.data?.data;

  // Handle both paginated { applications: [...], total: N } and direct array responses
  const applications: Array<{
    id: number;
    job_title?: string;
    company_name?: string;
    status: string;
    created_at: string;
    updated_at: string;
  }> = Array.isArray(raw) ? raw : Array.isArray(raw?.applications) ? raw.applications : [];

  if (applications.length === 0) {
    return [];
  }

  // Transform applications into activity items
  const statusLabels: Record<string, { type: ActivityItem["type"]; title: string }> = {
    sent: { type: "application", title: "Application Sent" },
    delivered: { type: "application", title: "Application Delivered" },
    opened: { type: "application", title: "Application Opened" },
    replied: { type: "application", title: "Recipient Replied" },
    interview_scheduled: { type: "interview", title: "Interview Scheduled" },
    offer_received: { type: "offer", title: "Offer Received" },
    rejected: { type: "application", title: "Application Status" },
  };

  return applications
    .filter((app) => app.status !== "draft" && app.status !== "withdrawn")
    .slice(0, limit)
    .map((app) => {
      const label = statusLabels[app.status] || { type: "application" as const, title: "Application Updated" };
      return {
        id: app.id,
        type: label.type,
        title: label.title,
        description: app.job_title
          ? `${label.title} for ${app.job_title}${app.company_name ? ` at ${app.company_name}` : ""}`
          : label.title,
        timestamp: app.updated_at || app.created_at,
        application_id: app.id,
      };
    });
}
