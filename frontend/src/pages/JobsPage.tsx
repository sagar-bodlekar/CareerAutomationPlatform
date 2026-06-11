import { useState } from "react";
import { Link } from "react-router-dom";
import { Search, MapPin, Clock, Briefcase, SlidersHorizontal } from "lucide-react";

const mockJobs = [
  { id: 1, title: "Senior Software Engineer", company: "Tech Corp", location: "San Francisco, CA", type: "Full-time", salary: "$150k - $200k", skills: ["Python", "React", "AWS"], matchScore: 92, posted: "2d ago", logo: "TC" },
  { id: 2, title: "Frontend Engineer", company: "Startup Inc", location: "Remote", type: "Full-time", salary: "$120k - $160k", skills: ["React", "TypeScript", "GraphQL"], matchScore: 88, posted: "1d ago", logo: "SI" },
  { id: 3, title: "Backend Developer", company: "DataFlow", location: "New York, NY", type: "Contract", salary: "$130k - $170k", skills: ["Go", "PostgreSQL", "Docker"], matchScore: 76, posted: "3d ago", logo: "DF" },
  { id: 4, title: "ML Engineer", company: "AI Labs", location: "Remote", type: "Full-time", salary: "$160k - $220k", skills: ["Python", "TensorFlow", "MLOps"], matchScore: 65, posted: "4d ago", logo: "AL" },
  { id: 5, title: "DevOps Engineer", company: "CloudScale", location: "Austin, TX", type: "Full-time", salary: "$140k - $180k", skills: ["AWS", "Kubernetes", "Terraform"], matchScore: 82, posted: "1d ago", logo: "CS" },
  { id: 6, title: "Full Stack Developer", company: "WebFlow", location: "Remote", type: "Part-time", salary: "$80k - $110k", skills: ["React", "Node.js", "MongoDB"], matchScore: 71, posted: "5d ago", logo: "WF" },
];

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 85 ? "bg-green-100 text-green-700" : score >= 70 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700";
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${color}`}>{score}%</span>;
}

export default function JobsPage() {
  const [query, setQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
        <p className="text-gray-500">Discover opportunities matched to your profile</p>
      </div>

      {/* Search + filters */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search jobs by title, company, or skills..."
            className="block w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-50"
        >
          <SlidersHorizontal className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <div className="grid gap-4 sm:grid-cols-4">
            <div>
              <label className="block text-xs font-medium text-gray-600">Location Type</label>
              <select className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                <option>All</option>
                <option>Remote</option>
                <option>Hybrid</option>
                <option>On-site</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Employment Type</label>
              <select className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
                <option>All</option>
                <option>Full-time</option>
                <option>Part-time</option>
                <option>Contract</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Salary Min</label>
              <input type="number" placeholder="$80k" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600">Salary Max</label>
              <input type="number" placeholder="$250k" className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>
        </div>
      )}

      {/* Job list */}
      <div className="space-y-3">
        {mockJobs.map((job) => (
          <Link
            key={job.id}
            to={`/jobs/${job.id}`}
            className="group block rounded-xl border bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-200"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 text-sm font-bold text-white shadow-sm">
                {job.logo}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{job.title}</h3>
                    <p className="text-sm text-gray-500">{job.company}</p>
                  </div>
                  <ScoreBadge score={job.matchScore} />
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> {job.location}</span>
                  <span className="flex items-center gap-1"><Briefcase className="h-3 w-3" /> {job.type}</span>
                  <span className="flex items-center gap-1">💰 {job.salary}</span>
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {job.posted}</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {job.skills.map((skill) => (
                    <span key={skill} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{skill}</span>
                  ))}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
