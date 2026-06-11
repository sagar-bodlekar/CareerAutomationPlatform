import { Link } from "react-router-dom";
import { FileText, Plus, Download, Sparkles, BarChart3 } from "lucide-react";

const mockResumes = [
  { id: 1, title: "Master Resume", type: "master", role: "Full Stack Developer", version: 3, atsScore: 82, updated: "2d ago" },
  { id: 2, title: "Frontend Engineer - Tech Corp", type: "role-specific", role: "Frontend Engineer", version: 1, atsScore: 91, updated: "1d ago" },
  { id: 3, title: "Backend Developer - DataFlow", type: "role-specific", role: "Backend Developer", version: 1, atsScore: 78, updated: "3d ago" },
  { id: 4, title: "ATS Optimized - General", type: "ats-optimized", role: "Software Engineer", version: 2, atsScore: 94, updated: "5d ago" },
];

function ResumeCard({ resume }: { resume: typeof mockResumes[0] }) {
  const typeColors: Record<string, string> = {
    master: "bg-purple-100 text-purple-700",
    "role-specific": "bg-blue-100 text-blue-700",
    "ats-optimized": "bg-green-100 text-green-700",
  };

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
            <p className="text-sm text-gray-500">{resume.role}</p>
          </div>
        </div>
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${typeColors[resume.type] || "bg-gray-100 text-gray-700"}`}>
          {resume.type.replace("-", " ")}
        </span>
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
        <span>v{resume.version}</span>
        <span>Updated {resume.updated}</span>
        {resume.atsScore && (
          <span className={`flex items-center gap-1 font-medium ${resume.atsScore >= 90 ? "text-green-600" : resume.atsScore >= 75 ? "text-yellow-600" : "text-red-500"}`}>
            <BarChart3 className="h-3 w-3" />
            ATS: {resume.atsScore}%
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

export default function ResumesPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resumes</h1>
          <p className="text-gray-500">Create and manage your role-specific resumes</p>
        </div>
        <Link
          to="/resumes/generate"
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700"
        >
          <Plus className="h-4 w-4" />
          Generate Resume
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {mockResumes.map((resume) => (
          <ResumeCard key={resume.id} resume={resume} />
        ))}
      </div>
    </div>
  );
}
