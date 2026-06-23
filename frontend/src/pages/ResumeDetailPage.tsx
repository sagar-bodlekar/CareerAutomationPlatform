import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Download, Sparkles, AlertCircle, FileText } from "lucide-react";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useResume } from "../hooks/useResumes";
import { optimizeResume, getResumeDownloadUrl } from "../services/resumes";
import { ProfileSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { capitalize } from "../utils/formatters";
import { getErrorMessage } from "../utils/errorHandler";

interface ContentBlock {
  summary?: string;
  experience?: Array<{
    company: string;
    title: string;
    period: string;
    bullets: string[];
  }>;
  education?: Array<{
    institution: string;
    degree?: string;
    year?: string;
  }>;
  skills?: string[];
}

function renderContent(content: Record<string, unknown>): ContentBlock {
  if (!content || typeof content !== "object") return {};
  return content as unknown as ContentBlock;
}

export default function ResumeDetailPage() {
  useDocumentTitle("Resume Details");
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const resumeId = id ?? "";

  const {
    data: resume,
    isLoading,
    isError,
    error,
    refetch,
  } = useResume(resumeId);

  const [optimizing, setOptimizing] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const handleOptimize = async () => {
    setOptimizing(true);
    setActionError(null);
    try {
      await optimizeResume(resumeId);
      refetch();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setOptimizing(false);
    }
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const url = await getResumeDownloadUrl(resumeId);
      window.open(url, "_blank");
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setDownloading(false);
    }
  };

  // --- Loading state ---
  if (isLoading) {
    return (
      <div className="animate-fade-in">
        <ProfileSkeleton />
      </div>
    );
  }

  // --- Error state ---
  if (isError) {
    return (
      <div className="animate-fade-in space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" /> Back to resumes
        </button>
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  // --- Not found state ---
  if (!resume) {
    return (
      <div className="animate-fade-in space-y-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" /> Back to resumes
        </button>
        <div className="flex flex-col items-center justify-center rounded-xl border bg-white p-12 shadow-sm">
          <AlertCircle className="mb-4 h-12 w-12 text-gray-300" />
          <h2 className="mb-2 text-lg font-semibold text-gray-900">Resume not found</h2>
          <p className="mb-6 text-sm text-gray-500">This resume may have been deleted or is no longer available.</p>
          <Link to="/resumes" className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700">
            View All Resumes
          </Link>
        </div>
      </div>
    );
  }

  // --- Populated state ---
  const content = renderContent(resume.content);

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{resume.title}</h1>
          <p className="text-gray-500">
            {resume.target_role ? `${resume.target_role} · ` : ""}v{resume.version} · {capitalize(resume.resume_type)}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleOptimize}
            disabled={optimizing}
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            {optimizing ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {optimizing ? "Optimizing..." : "Optimize ATS"}
          </button>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            {downloading ? "Opening..." : "Download PDF"}
          </button>
        </div>
      </div>

      {actionError && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {actionError}
        </div>
      )}

      {/* ATS Score */}
      {resume.ats_score !== null && resume.ats_score !== undefined && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className={`flex h-20 w-20 items-center justify-center rounded-full ${resume.ats_score >= 85 ? "bg-green-50" : resume.ats_score >= 70 ? "bg-blue-50" : "bg-amber-50"}`}>
              <span className={`text-2xl font-bold ${resume.ats_score >= 85 ? "text-green-600" : resume.ats_score >= 70 ? "text-blue-600" : "text-amber-600"}`}>
                {resume.ats_score}%
              </span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">ATS Compatibility Score</h3>
              <p className="text-sm text-gray-500">
                {resume.ats_score >= 85
                  ? "Your resume scores well with applicant tracking systems. Consider targeting specific roles to further improve."
                  : resume.ats_score >= 70
                  ? "Your resume has good ATS compatibility. Optimizing for specific roles can boost your score further."
                  : "Consider optimizing your resume for better ATS compatibility and higher match rates."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Resume content preview */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        {/* Summary */}
        {content.summary && (
          <div className="mb-6">
            <p className="text-sm text-gray-700">{content.summary}</p>
          </div>
        )}

        {/* Experience */}
        {content.experience && content.experience.length > 0 && (
          <div className="mb-6">
            <h3 className="mb-3 text-lg font-semibold text-gray-900">Experience</h3>
            {content.experience.map((exp, i) => (
              <div key={i} className="mb-4 border-l-2 border-primary-200 pl-4">
                <p className="font-semibold text-gray-900">{exp.title}</p>
                <p className="text-sm text-gray-500">{exp.company}{exp.period ? ` · ${exp.period}` : ""}</p>
                {exp.bullets && exp.bullets.length > 0 && (
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-gray-600">
                    {exp.bullets.map((b, j) => <li key={j}>{b}</li>)}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Skills */}
        {content.skills && content.skills.length > 0 && (
          <div className="mb-6">
            <h3 className="mb-3 text-lg font-semibold text-gray-900">Skills</h3>
            <div className="flex flex-wrap gap-2">
              {content.skills.map((s) => (
                <span key={s} className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700">{s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Education */}
        {content.education && content.education.length > 0 && (
          <div>
            <h3 className="mb-3 text-lg font-semibold text-gray-900">Education</h3>
            {content.education.map((edu, i) => (
              <div key={i} className="mb-3 last:mb-0">
                <p className="font-medium text-gray-900">{edu.institution}</p>
                <p className="text-sm text-gray-500">
                  {edu.degree}{edu.year ? ` · ${edu.year}` : ""}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Empty state for no content */}
        {Object.keys(content).length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <FileText className="mb-2 h-8 w-8" />
            <p className="text-sm">No content available for this resume</p>
          </div>
        )}
      </div>
    </div>
  );
}
