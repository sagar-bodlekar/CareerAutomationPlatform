import { Link } from "react-router-dom";
import { MapPin, Briefcase, Clock } from "lucide-react";
import type { Job } from "../../types";
import MatchScoreBadge from "./MatchScoreBadge";

interface Props {
  job: Job;
  matchScore?: number;
  logo?: string;
}

export default function JobCard({ job, matchScore, logo }: Props) {
  return (
    <Link
      to={`/jobs/${job.id}`}
      className="group block rounded-xl border bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-200"
    >
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 text-sm font-bold text-white shadow-sm">
          {logo || (job.company_name?.charAt(0) ?? "?")}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{job.title}</h3>
              <p className="text-sm text-gray-500">{job.company_name}</p>
            </div>
            {matchScore !== undefined && <MatchScoreBadge score={matchScore} />}
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {job.location}</span>
            <span className="flex items-center gap-1"><Briefcase className="h-3 w-3" /> {job.employment_type}</span>
            {job.salary_min && <span>💰 ${job.salary_min.toLocaleString()} - ${job.salary_max?.toLocaleString()}</span>}
            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {new Date(job.posted_date).toLocaleDateString()}</span>
          </div>
          {job.required_skills && job.required_skills.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {job.required_skills.slice(0, 4).map((skill) => (
                <span key={skill} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{skill}</span>
              ))}
              {job.required_skills.length > 4 && (
                <span className="text-xs text-gray-400">+{job.required_skills.length - 4} more</span>
              )}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
