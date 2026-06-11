import { Link } from "react-router-dom";
import { ArrowLeft, Globe, Clock, Percent, BarChart3 } from "lucide-react";
import SourceBreakdown from "../components/tracking/SourceBreakdown";
import ApplicationFunnel from "../components/tracking/ApplicationFunnel";

const mockSources = [
  { source: "LinkedIn", count: 10, interview_count: 3, success_rate: 30 },
  { source: "Wellfound", count: 6, interview_count: 2, success_rate: 33.3 },
  { source: "Naukri", count: 5, interview_count: 1, success_rate: 20 },
  { source: "RemoteOK", count: 4, interview_count: 0, success_rate: 0 },
  { source: "Company Websites", count: 3, interview_count: 2, success_rate: 66.7 },
];

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

export default function AnalyticsPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/tracking" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500">Detailed breakdown of your application performance</p>
        </div>
      </div>

      {/* Key metrics */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
              <Percent className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Response Rate</p>
              <p className="text-xl font-bold text-gray-900">50%</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
              <Clock className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg Response Time</p>
              <p className="text-xl font-bold text-gray-900">3.2 days</p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100">
              <BarChart3 className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Interview Rate</p>
              <p className="text-xl font-bold text-gray-900">25%</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Funnel */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Application Funnel</h2>
          <ApplicationFunnel data={mockFunnel} />
        </div>

        {/* Source breakdown */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <Globe className="h-5 w-5 text-gray-500" /> Source Performance
          </h2>
          <SourceBreakdown data={mockSources} />
        </div>
      </div>
    </div>
  );
}
