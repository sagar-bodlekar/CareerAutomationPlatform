import { Link } from "react-router-dom";
import { FileText, Download, Sparkles, BarChart3 } from "lucide-react";
import type { Resume } from "../../types";

interface Props {
  resume: Resume;
}

const typeColors: Record<string, string> = {
  master: "bg-purple-100 text-purple-700",
  "role-specific": "bg-blue-100 text-blue-700",
  "ats-optimized": "bg-green-100 text-green-700",
};

export default function ResumeCard({ resume }: Props) {
  return (
    <div className="group rounded-xl border bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-200">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-400 to-indigo-600 text-white shadow-sm">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <Link to={`/resumes/${resume.id}`} className="font-semibold text-gray-900 hover:text-primary-600 transition-colors">
              {resume.title}
            </Link>
            {resume.target_role && <p className="text-sm text-gray-500">{resume.target_role}</p>}
          </div>
        </div>
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${typeColors[resume.resume_type] || "bg-gray-100 text-gray-700"}`}>
          {resume.resume_type.replace("-", " ")}
        </span>
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
        <span>v{resume.version}</span>
        <span>Updated {new Date(resume.updated_at).toLocaleDateString()}</span>
        {resume.ats_score !== null && resume.ats_score !== undefined && (
          <span className={`flex items-center gap-1 font-medium ${resume.ats_score >= 90 ? "text-green-600" : resume.ats_score >= 75 ? "text-yellow-600" : "text-red-500"}`}>
            <BarChart3 className="h-3 w-3" />
            ATS: {resume.ats_score}%
          </span>
        )}
      </div>

      <div className="mt-4 flex gap-2">
        <button className="flex items-center gap-1 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition-colors">
          <Download className="h-3 w-3" /> Download PDF
        </button>
        <button className="flex items-center gap-1 rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition-colors">
          <Sparkles className="h-3 w-3" /> Optimize
        </button>
      </div>
    </div>
  );
}
