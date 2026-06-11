import { Link } from "react-router-dom";
import {
  Mail,
  MapPin,
  Github,
  Linkedin,
  Edit3,
  Award,
  BookOpen,
  FolderGit2,
  Briefcase,
} from "lucide-react";

const mockProfile = {
  personal_info: { full_name: "Alex Johnson", email: "alex@example.com", location: "San Francisco, CA", headline: "Senior Full Stack Engineer" },
  skills: [
    { name: "Python", category: "technical", proficiency: "expert" },
    { name: "React", category: "technical", proficiency: "advanced" },
    { name: "TypeScript", category: "technical", proficiency: "advanced" },
    { name: "AWS", category: "technical", proficiency: "intermediate" },
    { name: "PostgreSQL", category: "technical", proficiency: "advanced" },
    { name: "Docker", category: "technical", proficiency: "intermediate" },
    { name: "GraphQL", category: "technical", proficiency: "intermediate" },
    { name: "Leadership", category: "soft", proficiency: "advanced" },
  ],
  experiences: [
    { company_name: "Tech Corp", title: "Senior Engineer", start_date: "2022-01", end_date: null, is_current: true, description: "Building scalable microservices" },
    { company_name: "Startup Inc", title: "Full Stack Developer", start_date: "2019-03", end_date: "2021-12", is_current: false, description: "Led frontend team" },
  ],
  education: [
    { institution: "MIT", degree: "B.S.", field: "Computer Science", start_date: "2015", end_date: "2019" },
  ],
};

function Badge({ children, variant = "default" }: { children: React.ReactNode; variant?: string }) {
  const colors: Record<string, string> = {
    expert: "bg-purple-100 text-purple-700",
    advanced: "bg-blue-100 text-blue-700",
    intermediate: "bg-green-100 text-green-700",
    beginner: "bg-gray-100 text-gray-600",
    technical: "bg-indigo-100 text-indigo-700",
    soft: "bg-amber-100 text-amber-700",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[variant] || "bg-gray-100 text-gray-700"}`}>
      {children}
    </span>
  );
}

export default function ProfilePage() {
  const p = mockProfile;

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
          <p className="text-gray-500">Your career single source of truth</p>
        </div>
        <Link
          to="/profile/edit"
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700"
        >
          <Edit3 className="h-4 w-4" />
          Edit Profile
        </Link>
      </div>

      {/* Personal info card */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 text-2xl font-bold text-white shadow-md">
            {p.personal_info.full_name.charAt(0)}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">{p.personal_info.full_name}</h2>
            <p className="text-primary-600 font-medium">{p.personal_info.headline}</p>
            <div className="mt-2 flex flex-wrap gap-3 text-sm text-gray-500">
              <span className="flex items-center gap-1"><Mail className="h-3.5 w-3.5" /> {p.personal_info.email}</span>
              <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {p.personal_info.location}</span>
              <span className="flex items-center gap-1"><Linkedin className="h-3.5 w-3.5" /> linkedin.com/in/alex</span>
              <span className="flex items-center gap-1"><Github className="h-3.5 w-3.5" /> github.com/alex</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Skills */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <Award className="h-5 w-5 text-amber-500" /> Skills
          </h3>
          <div className="space-y-3">
            {p.skills.map((skill, i) => (
              <div key={i} className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-gray-900">{skill.name}</span>
                  <Badge variant={skill.category}>{skill.category}</Badge>
                </div>
                <Badge variant={skill.proficiency}>{skill.proficiency}</Badge>
              </div>
            ))}
          </div>
          <Link to="/profile/skills" className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500">
            Manage skills →
          </Link>
        </div>

        {/* Experience */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <Briefcase className="h-5 w-5 text-blue-500" /> Experience
          </h3>
          <div className="space-y-4">
            {p.experiences.map((exp, i) => (
              <div key={i} className="border-l-2 border-primary-200 pl-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{exp.title}</p>
                    <p className="text-sm text-gray-500">{exp.company_name}</p>
                  </div>
                  {exp.is_current && <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">Current</span>}
                </div>
                <p className="mt-1 text-xs text-gray-400">{exp.start_date} – {exp.end_date || "Present"}</p>
                <p className="mt-1 text-sm text-gray-600">{exp.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Education */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <BookOpen className="h-5 w-5 text-green-500" /> Education
          </h3>
          {p.education.map((edu, i) => (
            <div key={i} className="border-l-2 border-green-200 pl-4">
              <p className="font-semibold text-gray-900">{edu.institution}</p>
              <p className="text-sm text-gray-600">{edu.degree} in {edu.field}</p>
              <p className="text-xs text-gray-400">{edu.start_date} – {edu.end_date}</p>
            </div>
          ))}
        </div>

        {/* Projects */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <FolderGit2 className="h-5 w-5 text-purple-500" /> Projects
          </h3>
          <div className="flex items-center justify-center py-8 text-sm text-gray-400">
            <p>Add projects to showcase your work</p>
          </div>
        </div>
      </div>
    </div>
  );
}
