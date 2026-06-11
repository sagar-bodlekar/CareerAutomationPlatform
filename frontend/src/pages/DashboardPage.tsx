import { Link } from "react-router-dom";
import {
  Briefcase,
  FileText,
  Send,
  TrendingUp,
  Users,
  Clock,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  value: string | number;
  trend?: string;
  color: string;
}

function StatCard({ icon: Icon, label, value, trend, color }: StatCardProps) {
  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-center gap-4">
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && <p className="text-xs text-green-600">{trend}</p>}
        </div>
      </div>
    </div>
  );
}

const recentActivity = [
  { icon: Briefcase, text: "New job match: Senior Engineer at Tech Corp", time: "2h ago", color: "bg-blue-500" },
  { icon: FileText, text: "Resume generated for Frontend Developer role", time: "5h ago", color: "bg-indigo-500" },
  { icon: Send, text: "Application sent to Data Scientist at AI Co", time: "1d ago", color: "bg-cyan-500" },
  { icon: TrendingUp, text: "Match score improved by 15% after ATS optimization", time: "2d ago", color: "bg-green-500" },
  { icon: Clock, text: "Interview scheduled with Startup Inc", time: "3d ago", color: "bg-amber-500" },
];

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome{user?.email ? `, ${user.email.split("@")[0]}` : ""}
        </h1>
        <p className="mt-1 text-gray-500">Here's your career activity overview</p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Briefcase} label="Active Applications" value={12} trend="+3 this week" color="bg-blue-600" />
        <StatCard icon={FileText} label="Resumes Ready" value={4} trend="2 optimized" color="bg-indigo-600" />
        <StatCard icon={Send} label="Applications Sent" value={28} trend="85% delivery rate" color="bg-cyan-600" />
        <StatCard icon={Users} label="Job Matches" value={47} trend="18 new today" color="bg-green-600" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Quick actions */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Actions</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <Link
              to="/jobs"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700"
            >
              <Briefcase className="h-5 w-5" />
              Browse Jobs
            </Link>
            <Link
              to="/resumes"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-700"
            >
              <FileText className="h-5 w-5" />
              Manage Resumes
            </Link>
            <Link
              to="/applications"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-cyan-50 hover:border-cyan-200 hover:text-cyan-700"
            >
              <Send className="h-5 w-5" />
              View Applications
            </Link>
            <Link
              to="/profile/edit"
              className="flex items-center gap-3 rounded-lg border bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-amber-50 hover:border-amber-200 hover:text-amber-700"
            >
              <Users className="h-5 w-5" />
              Edit Profile
            </Link>
          </div>
        </div>

        {/* Recent activity */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${item.color}`}>
                  <item.icon className="h-4 w-4 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700">{item.text}</p>
                  <p className="text-xs text-gray-400">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
