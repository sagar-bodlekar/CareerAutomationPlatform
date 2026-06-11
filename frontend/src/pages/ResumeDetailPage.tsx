import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Download, Sparkles } from "lucide-react";

const mockResume = {
  id: 1,
  title: "Master Resume",
  type: "master",
  role: "Full Stack Developer",
  version: 3,
  atsScore: 82,
  content: {
    summary: "Experienced full stack engineer with 6+ years building scalable web applications.",
    experience: [
      { company: "Tech Corp", title: "Senior Engineer", period: "2022 - Present", bullets: ["Led migration to microservices", "Improved API latency by 40%", "Mentored 3 junior engineers"] },
      { company: "Startup Inc", title: "Full Stack Developer", period: "2019 - 2021", bullets: ["Built React frontend from scratch", "Designed GraphQL API", "Managed CI/CD pipeline"] },
    ],
    education: [{ institution: "MIT", degree: "B.S. Computer Science", year: "2019" }],
    skills: ["Python", "React", "TypeScript", "AWS", "PostgreSQL", "Docker", "GraphQL"],
  },
};

export default function ResumeDetailPage() {
  const navigate = useNavigate();
  const [optimizing, setOptimizing] = useState(false);

  const handleOptimize = async () => {
    setOptimizing(true);
    await new Promise((r) => setTimeout(r, 1500));
    setOptimizing(false);
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{mockResume.title}</h1>
          <p className="text-gray-500">{mockResume.role} · v{mockResume.version}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleOptimize}
            disabled={optimizing}
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            {optimizing ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            Optimize ATS
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700">
            <Download className="h-4 w-4" />
            Download PDF
          </button>
        </div>
      </div>

      {/* ATS Score */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center gap-4">
          <div className={`flex h-20 w-20 items-center justify-center rounded-full ${mockResume.atsScore >= 85 ? "bg-green-50" : "bg-yellow-50"}`}>
            <span className={`text-2xl font-bold ${mockResume.atsScore >= 85 ? "text-green-600" : "text-yellow-600"}`}>{mockResume.atsScore}%</span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">ATS Compatibility Score</h3>
            <p className="text-sm text-gray-500">Your resume scores well with applicant tracking systems. Consider optimizing for specific roles to improve further.</p>
          </div>
        </div>
      </div>

      {/* Resume content preview */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900">Alex Johnson</h2>
          <p className="text-gray-500">alex@example.com · San Francisco, CA</p>
          <p className="mt-3 text-sm text-gray-700">{mockResume.content.summary}</p>
        </div>

        {/* Experience */}
        <div className="mb-6">
          <h3 className="mb-3 text-lg font-semibold text-gray-900">Experience</h3>
          {mockResume.content.experience.map((exp, i) => (
            <div key={i} className="mb-4 border-l-2 border-primary-200 pl-4">
              <p className="font-semibold text-gray-900">{exp.title}</p>
              <p className="text-sm text-gray-500">{exp.company} · {exp.period}</p>
              <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-gray-600">
                {exp.bullets.map((b, j) => <li key={j}>{b}</li>)}
              </ul>
            </div>
          ))}
        </div>

        {/* Skills */}
        <div className="mb-6">
          <h3 className="mb-3 text-lg font-semibold text-gray-900">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {mockResume.content.skills.map((s) => (
              <span key={s} className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700">{s}</span>
            ))}
          </div>
        </div>

        {/* Education */}
        <div>
          <h3 className="mb-3 text-lg font-semibold text-gray-900">Education</h3>
          {mockResume.content.education.map((edu, i) => (
            <div key={i}>
              <p className="font-medium text-gray-900">{edu.institution}</p>
              <p className="text-sm text-gray-500">{edu.degree} · {edu.year}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
