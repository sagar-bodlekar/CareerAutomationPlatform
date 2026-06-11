import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Send,
  Eye,
  MessageCircle,
  CalendarCheck,
  Target,
  TrendingUp,
  Download,
  BarChart3,
  Bell,
} from "lucide-react";
import StatsCard from "../components/tracking/StatsCard";
import ApplicationFunnel from "../components/tracking/ApplicationFunnel";
import DailyChart from "../components/tracking/DailyChart";

const mockStats = {
  total_applications: 28,
  total_sent: 24,
  total_delivered: 22,
  total_opened: 18,
  total_replied: 12,
  total_interviews: 6,
  total_offers: 2,
  total_rejected: 3,
  avg_match_score: 78,
  success_rate: 25,
};

const mockFunnel = [
  { status: "draft", label: "Draft", count: 4, percentage: 14.3 },
  { status: "sent", label: "Sent", count: 24, percentage: 85.7 },
  { status: "delivered", label: "Delivered", count: 22, percentage: 78.6 },
  { status: "opened", label: "Opened", count: 18, percentage: 64.3 },
  { status: "replied", label: "Replied", count: 12, percentage: 42.9 },
  { status: "interview_scheduled", label: "Interview", count: 6, percentage: 21.4 },
  { status: "offer_received", label: "Offer", count: 2, percentage: 7.1 },
  { status: "rejected", label: "Rejected", count: 3, percentage: 10.7 },
];

const mockTrends = Array.from({ length: 30 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() - (29 - i));
  return {
    date: d.toISOString().slice(0, 10),
    count: Math.floor(Math.random() * 4),
    sent_count: Math.floor(Math.random() * 3),
    interview_count: 0,
    offer_count: 0,
  };
});

export default function TrackingPage() {
  const [exporting, setExporting] = useState(false);

  const handleExport = async (_format: "csv" | "json") => {
    setExporting(true);
    await new Promise((r) => setTimeout(r, 1000));
    setExporting(false);
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tracking Dashboard</h1>
          <p className="text-gray-500">Monitor your application pipeline performance</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/tracking/analytics"
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <BarChart3 className="h-4 w-4" />
            Analytics
          </Link>
          <Link
            to="/tracking/notifications"
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Bell className="h-4 w-4" />
            Notifications
          </Link>
          <button
            onClick={() => handleExport("csv")}
            disabled={exporting}
            className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            {exporting ? "Exporting..." : "Export"}
          </button>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard icon={<Send className="h-6 w-6 text-white" />} label="Total Sent" value={mockStats.total_sent} subtext="24 of 28 applications" color="bg-blue-600" />
        <StatsCard icon={<Eye className="h-6 w-6 text-white" />} label="Opened" value={mockStats.total_opened} subtext={`${Math.round((mockStats.total_opened / mockStats.total_sent) * 100)}% open rate`} color="bg-emerald-600" />
        <StatsCard icon={<MessageCircle className="h-6 w-6 text-white" />} label="Replied" value={mockStats.total_replied} subtext={`${Math.round((mockStats.total_replied / mockStats.total_sent) * 100)}% reply rate`} color="bg-green-600" />
        <StatsCard icon={<CalendarCheck className="h-6 w-6 text-white" />} label="Interviews" value={mockStats.total_interviews} subtext={`${mockStats.success_rate}% success rate`} color="bg-lime-600" />
        <StatsCard icon={<Target className="h-6 w-6 text-white" />} label="Avg Match Score" value={`${mockStats.avg_match_score}%`} subtext="Across all applications" color="bg-indigo-600" />
        <StatsCard icon={<TrendingUp className="h-6 w-6 text-white" />} label="Offers" value={mockStats.total_offers} subtext={`${Math.round((mockStats.total_offers / mockStats.total_sent) * 100)}% conversion`} color="bg-amber-600" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Funnel */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Application Funnel</h2>
          <ApplicationFunnel data={mockFunnel} />
        </div>

        {/* Daily trends */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Daily Activity (30 days)</h2>
          <DailyChart data={mockTrends} />
          <div className="mt-4 flex items-center justify-center gap-6 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <span className="inline-block h-3 w-3 rounded bg-primary-400" /> Applications
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
