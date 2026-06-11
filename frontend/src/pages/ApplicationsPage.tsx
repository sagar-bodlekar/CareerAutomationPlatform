import { useState } from "react";
import { Link } from "react-router-dom";
import { Send, Building2, ChevronRight } from "lucide-react";

const mockApps = [
  { id: 1, company: "Tech Corp", role: "Senior Software Engineer", status: "sent", progress: 50, updated: "2h ago", matchScore: 92 },
  { id: 2, company: "DataFlow", role: "Backend Developer", status: "draft", progress: 0, updated: "1d ago", matchScore: 76 },
  { id: 3, company: "Startup Inc", role: "Frontend Engineer", status: "delivered", progress: 60, updated: "4h ago", matchScore: 88 },
  { id: 4, company: "AI Labs", role: "ML Engineer", status: "interview_scheduled", progress: 85, updated: "1d ago", matchScore: 65 },
  { id: 5, company: "CloudScale", role: "DevOps Engineer", status: "opened", progress: 70, updated: "3d ago", matchScore: 82 },
  { id: 6, company: "Tech Corp", role: "Staff Engineer", status: "offer_received", progress: 95, updated: "5d ago", matchScore: 90 },
];

const statusConfig: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-gray-100 text-gray-700" },
  matched: { label: "Matched", color: "bg-blue-100 text-blue-700" },
  resume_generated: { label: "Resume Ready", color: "bg-indigo-100 text-indigo-700" },
  cover_letter_generated: { label: "Letter Ready", color: "bg-purple-100 text-purple-700" },
  email_prepared: { label: "Email Ready", color: "bg-pink-100 text-pink-700" },
  sent: { label: "Sent", color: "bg-cyan-100 text-cyan-700" },
  delivered: { label: "Delivered", color: "bg-teal-100 text-teal-700" },
  opened: { label: "Opened", color: "bg-emerald-100 text-emerald-700" },
  replied: { label: "Replied", color: "bg-green-100 text-green-700" },
  interview_scheduled: { label: "Interview", color: "bg-lime-100 text-lime-700" },
  offer_received: { label: "Offer!", color: "bg-amber-100 text-amber-700" },
  rejected: { label: "Rejected", color: "bg-red-100 text-red-700" },
  withdrawn: { label: "Withdrawn", color: "bg-gray-200 text-gray-500" },
};

export default function ApplicationsPage() {
  const [filter, setFilter] = useState<string>("all");

  const filtered = filter === "all" ? mockApps : mockApps.filter((a) => a.status === filter);

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="text-gray-500">Track your job applications from draft to offer</p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {["all", "draft", "sent", "delivered", "opened", "replied", "interview_scheduled", "offer_received"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`whitespace-nowrap rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === s ? "bg-primary-600 text-white shadow-sm" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {s === "all" ? "All" : statusConfig[s]?.label || s}
          </button>
        ))}
      </div>

      {/* Application cards */}
      <div className="space-y-3">
        {filtered.map((app) => {
          const cfg = statusConfig[app.status] || { label: app.status, color: "bg-gray-100 text-gray-700" };
          return (
            <Link
              key={app.id}
              to={`/applications/${app.id}`}
              className="group block rounded-xl border bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-200"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-cyan-600 text-white shadow-sm">
                    <Send className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{app.role}</h3>
                    <p className="flex items-center gap-1 text-sm text-gray-500">
                      <Building2 className="h-3.5 w-3.5" /> {app.company}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>
                    {cfg.label}
                  </span>
                  <span className="text-sm font-semibold text-gray-400">{app.matchScore}%</span>
                  <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-gray-500 transition-colors" />
                </div>
              </div>

              {/* Progress bar */}
              <div className="mt-3">
                <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                  <span>Progress</span>
                  <span>{app.progress}%</span>
                </div>
                <div className="h-1.5 rounded-full bg-gray-100">
                  <div
                    className="h-1.5 rounded-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all"
                    style={{ width: `${app.progress}%` }}
                  />
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
