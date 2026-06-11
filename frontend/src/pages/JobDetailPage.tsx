import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, MapPin, Briefcase, Clock, ExternalLink, Send, BarChart3 } from "lucide-react";

const mockJob = {
  id: 1,
  title: "Senior Software Engineer",
  company: "Tech Corp",
  location: "San Francisco, CA",
  type: "Full-time",
  salary: "$150k - $200k",
  description: "We're looking for a Senior Software Engineer to join our core platform team. You'll be building scalable microservices, mentoring junior engineers, and driving architectural decisions.",
  requirements: "5+ years of software engineering experience\nStrong proficiency in Python and React\nExperience with cloud platforms (AWS/GCP)\nUnderstanding of distributed systems\nExcellent communication skills",
  skills: ["Python", "React", "AWS", "PostgreSQL", "Docker"],
  matchScore: 92,
  posted: "2 days ago",
};

export default function JobDetailPage() {
  const navigate = useNavigate();
  const [applying, setApplying] = useState(false);

  const handleApply = async () => {
    setApplying(true);
    await new Promise((r) => setTimeout(r, 1000));
    setApplying(false);
    navigate("/applications");
  };

  return (
    <div className="animate-fade-in space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to jobs
      </button>

      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 text-xl font-bold text-white shadow-md">
              TC
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{mockJob.title}</h1>
              <p className="text-lg text-gray-500">{mockJob.company}</p>
              <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1"><MapPin className="h-4 w-4" /> {mockJob.location}</span>
                <span className="flex items-center gap-1"><Briefcase className="h-4 w-4" /> {mockJob.type}</span>
                <span className="flex items-center gap-1">💰 {mockJob.salary}</span>
                <span className="flex items-center gap-1"><Clock className="h-4 w-4" /> {mockJob.posted}</span>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-center gap-1">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
              <span className="text-xl font-bold text-green-600">{mockJob.matchScore}%</span>
            </div>
            <span className="text-xs text-gray-400">Match</span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* Description */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Description</h2>
            <p className="text-sm text-gray-600 whitespace-pre-line">{mockJob.description}</p>
          </div>

          {/* Requirements */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold text-gray-900">Requirements</h2>
            <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
              {mockJob.requirements.split("\n").map((req, i) => (
                <li key={i}>{req}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-semibold text-gray-900">Actions</h3>
            <div className="space-y-3">
              <button
                onClick={handleApply}
                disabled={applying}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 disabled:opacity-50"
              >
                {applying ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {applying ? "Creating application..." : "Apply Now"}
              </button>
              <button className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50">
                <BarChart3 className="h-4 w-4" />
                View Match Details
              </button>
              <button className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50">
                <ExternalLink className="h-4 w-4" />
                View Original Posting
              </button>
            </div>
          </div>

          {/* Skills */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-semibold text-gray-900">Required Skills</h3>
            <div className="flex flex-wrap gap-2">
              {mockJob.skills.map((skill) => (
                <span key={skill} className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">{skill}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
