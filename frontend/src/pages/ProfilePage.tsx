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
  UserPlus,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useProfile } from "../hooks/useProfile";
import ExperienceTimeline from "../components/profile/ExperienceTimeline";
import { ProfileSkeleton } from "../components/common/Skeletons";
import { ErrorFallback } from "../components/common/ErrorFallback";
import { getErrorMessage, isNotFoundError } from "../utils/errorHandler";

const categoryColors: Record<string, string> = {
  technical: "bg-indigo-100 text-indigo-700",
  soft: "bg-amber-100 text-amber-700",
  domain: "bg-emerald-100 text-emerald-700",
  language: "bg-pink-100 text-pink-700",
};

const proficiencyColors: Record<string, string> = {
  expert: "bg-purple-100 text-purple-700",
  advanced: "bg-blue-100 text-blue-700",
  intermediate: "bg-green-100 text-green-700",
  beginner: "bg-gray-100 text-gray-600",
};

function Badge({ children, variant = "default" }: { children: React.ReactNode; variant?: string }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${proficiencyColors[variant] || categoryColors[variant] || "bg-gray-100 text-gray-700"}`}>
      {children}
    </span>
  );
}

export default function ProfilePage() {
  const { user } = useAuth();
  const {
    data: profile,
    isLoading,
    isError,
    error,
    refetch,
  } = useProfile(user?.id ?? "");

  // Loading state
  if (isLoading) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
            <p className="text-gray-500">Your career single source of truth</p>
          </div>
        </div>
        <ProfileSkeleton />
      </div>
    );
  }

  // Error OR empty state
  // Treat 404 (profile not found) as "no profile yet" — show the empty state
  if (isError && !isNotFoundError(error)) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
            <p className="text-gray-500">Your career single source of truth</p>
          </div>
        </div>
        <ErrorFallback
          message={getErrorMessage(error)}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  // Empty state — new user, no profile yet (also reached on 404)
  if (!profile) {
    return (
      <div className="animate-fade-in space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
            <p className="text-gray-500">Your career single source of truth</p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white py-16 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-100 mb-4">
            <UserPlus className="h-6 w-6 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Set up your profile</h3>
          <p className="mt-1 text-sm text-gray-500 max-w-sm">
            Create your career profile to unlock job matching, resume generation, and more.
          </p>
          <Link
            to="/profile/edit"
            className="mt-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 transition-colors"
          >
            Create Profile
          </Link>
        </div>
      </div>
    );
  }

  const pi = profile.personal_info;
  const displayName = pi?.full_name || user?.email?.split("@")[0] || "User";
  const initials = displayName.charAt(0).toUpperCase();

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
            {initials}
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900">{displayName}</h2>
            {profile.headline && (
              <p className="text-primary-600 font-medium">{profile.headline}</p>
            )}
            <div className="mt-2 flex flex-wrap gap-3 text-sm text-gray-500">
              {pi?.email && (
                <span className="flex items-center gap-1">
                  <Mail className="h-3.5 w-3.5" /> {pi.email}
                </span>
              )}
              {pi?.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" /> {pi.location}
                </span>
              )}
              {pi?.linkedin_url && (
                <span className="flex items-center gap-1">
                  <Linkedin className="h-3.5 w-3.5" /> {pi.linkedin_url.replace(/^https?:\/\//, "")}
                </span>
              )}
              {pi?.github_url && (
                <span className="flex items-center gap-1">
                  <Github className="h-3.5 w-3.5" /> {pi.github_url.replace(/^https?:\/\//, "")}
                </span>
              )}
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
          {profile.skills.length > 0 ? (
            <div className="space-y-3">
              {profile.skills.map((skill) => (
                <div key={skill.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900">{skill.name}</span>
                    <Badge variant={skill.category}>{skill.category}</Badge>
                  </div>
                  <Badge variant={skill.proficiency}>{skill.proficiency}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-6 text-center text-sm text-gray-400">
              No skills added yet.
            </div>
          )}
          <Link to="/profile/skills" className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500">
            Manage skills →
          </Link>
        </div>

        {/* Experience */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <Briefcase className="h-5 w-5 text-blue-500" /> Experience
          </h3>
          {(profile.work_experiences && profile.work_experiences.length > 0) ? (
            <ExperienceTimeline experiences={profile.work_experiences} />
          ) : (
            <div className="py-6 text-center text-sm text-gray-400">
              No work experience added yet.
            </div>
          )}
          <Link to="/profile/manage" className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-500">
            Manage all data →
          </Link>
        </div>

        {/* Education */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <BookOpen className="h-5 w-5 text-green-500" /> Education
          </h3>
          {profile.education.length > 0 ? (
            <div className="space-y-4">
              {profile.education.map((edu) => (
                <div key={edu.id} className="border-l-2 border-green-200 pl-4">
                  <p className="font-semibold text-gray-900">{edu.institution}</p>
                  {edu.degree && (
                    <p className="text-sm text-gray-600">
                      {edu.degree}{edu.field ? ` in ${edu.field}` : ""}
                    </p>
                  )}
                  {(edu.start_date || edu.end_date) && (
                    <p className="text-xs text-gray-400">
                      {edu.start_date || "—"} – {edu.end_date || "Present"}
                    </p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-6 text-center text-sm text-gray-400">
              No education added yet.
            </div>
          )}
        </div>

        {/* Projects */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
            <FolderGit2 className="h-5 w-5 text-purple-500" /> Projects
          </h3>
          {profile.projects && profile.projects.length > 0 ? (
            <div className="space-y-4">
              {profile.projects.map((project) => (
                <div key={project.id} className="border-l-2 border-purple-200 pl-4">
                  <p className="font-semibold text-gray-900">{project.name}</p>
                  {project.description && (
                    <p className="mt-1 text-sm text-gray-600">{project.description}</p>
                  )}
                  {project.technologies && project.technologies.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {project.technologies.map((tech) => (
                        <span key={tech} className="rounded-full bg-purple-50 px-2 py-0.5 text-xs text-purple-700">{tech}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-8 text-sm text-gray-400">
              Add projects to showcase your work
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
