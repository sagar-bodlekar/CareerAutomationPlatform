import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Search, X, Award } from "lucide-react";

const allSkills = [
  { name: "Python", category: "technical" },
  { name: "React", category: "technical" },
  { name: "TypeScript", category: "technical" },
  { name: "JavaScript", category: "technical" },
  { name: "AWS", category: "technical" },
  { name: "Docker", category: "technical" },
  { name: "PostgreSQL", category: "technical" },
  { name: "GraphQL", category: "technical" },
  { name: "Node.js", category: "technical" },
  { name: "Go", category: "technical" },
  { name: "Rust", category: "technical" },
  { name: "Kubernetes", category: "technical" },
  { name: "Leadership", category: "soft" },
  { name: "Communication", category: "soft" },
  { name: "Project Management", category: "soft" },
  { name: "Mentoring", category: "soft" },
  { name: "Machine Learning", category: "domain" },
  { name: "Data Engineering", category: "domain" },
  { name: "DevOps", category: "domain" },
];

function Badge({ children, color }: { children: React.ReactNode; color?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${color || "bg-gray-100 text-gray-700"}`}>
      {children}
    </span>
  );
}

export default function SkillsPage() {
  const [search, setSearch] = useState("");
  const [mySkills, setMySkills] = useState([
    { name: "Python", proficiency: "expert" },
    { name: "React", proficiency: "advanced" },
    { name: "TypeScript", proficiency: "advanced" },
    { name: "PostgreSQL", proficiency: "advanced" },
  ]);

  const filtered = allSkills.filter((s) => s.name.toLowerCase().includes(search.toLowerCase()) && !mySkills.find((ms) => ms.name === s.name));

  const addSkill = (name: string) => {
    setMySkills([...mySkills, { name, proficiency: "intermediate" }]);
  };

  const removeSkill = (name: string) => {
    setMySkills(mySkills.filter((s) => s.name !== name));
  };

  const setProficiency = (name: string, proficiency: string) => {
    setMySkills(mySkills.map((s) => (s.name === name ? { ...s, proficiency } : s)));
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
            <Award className="h-6 w-6 text-amber-500" /> Skills
          </h1>
          <p className="text-gray-500">Manage your skills and proficiencies</p>
        </div>
        <Link to="/profile" className="text-sm font-medium text-primary-600 hover:text-primary-500">
          ← Back to Profile
        </Link>
      </div>

      {/* My skills */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Your Skills ({mySkills.length})</h2>
        <div className="flex flex-wrap gap-2">
          {mySkills.map((skill) => (
            <Badge key={skill.name} color={skill.proficiency === "expert" ? "bg-purple-100 text-purple-700" : skill.proficiency === "advanced" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"}>
              {skill.name}
              <select
                value={skill.proficiency}
                onChange={(e) => setProficiency(skill.name, e.target.value)}
                className="ml-1 text-xs bg-transparent border-none outline-none cursor-pointer"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
              <button onClick={() => removeSkill(skill.name)} className="ml-1 hover:text-danger-500">
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      </div>

      {/* Add skills */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Add Skills</h2>
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search skills..."
            className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {filtered.map((skill) => (
            <button
              key={skill.name}
              onClick={() => addSkill(skill.name)}
              className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700 transition-colors hover:bg-primary-100 hover:text-primary-700"
            >
              <Plus className="h-3 w-3" />
              {skill.name}
              <span className="text-gray-400">({skill.category})</span>
            </button>
          ))}
          {filtered.length === 0 && search && (
            <p className="text-sm text-gray-400">No skills found</p>
          )}
        </div>
      </div>
    </div>
  );
}
