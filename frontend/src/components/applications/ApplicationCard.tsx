import { Link } from "react-router-dom";
import { Send, Building2, ChevronRight } from "lucide-react";
import type { Application } from "../../types";
import StatusBadge from "./StatusBadge";

interface Props {
  application: Application;
}

export default function ApplicationCard({ application }: Props) {
  return (
    <Link
      to={`/applications/${application.id}`}
      className="group block rounded-xl border bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-200"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-cyan-600 text-white shadow-sm">
            <Send className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{application.job_title}</h3>
            <p className="flex items-center gap-1 text-sm text-gray-500">
              <Building2 className="h-3.5 w-3.5" /> {application.company_name}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={application.status} />
          {application.match_score !== null && application.match_score !== undefined && (
            <span className="text-sm font-semibold text-gray-400">{Math.round(application.match_score)}%</span>
          )}
          <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-gray-500 transition-colors" />
        </div>
      </div>
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>{application.progress_percentage}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-gray-100">
          <div
            className="h-1.5 rounded-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all"
            style={{ width: `${application.progress_percentage}%` }}
          />
        </div>
      </div>
    </Link>
  );
}
