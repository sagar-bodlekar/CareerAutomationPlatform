import type { Skill } from "../../types";
import { X } from "lucide-react";

interface Props {
  skills: Skill[];
  onRemove?: (id: number) => void;
  readonly?: boolean;
}

const proficiencyColors: Record<string, string> = {
  expert: "bg-purple-100 text-purple-700",
  advanced: "bg-blue-100 text-blue-700",
  intermediate: "bg-green-100 text-green-700",
  beginner: "bg-gray-100 text-gray-600",
};

const categoryColors: Record<string, string> = {
  technical: "border-indigo-200",
  soft: "border-amber-200",
  domain: "border-emerald-200",
  language: "border-pink-200",
};

export default function SkillsList({ skills, onRemove, readonly }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill) => (
        <span
          key={skill.id}
          className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-sm ${
            proficiencyColors[skill.proficiency] || "bg-gray-100 text-gray-700"
          } ${categoryColors[skill.category] || ""}`}
        >
          {skill.name}
          <span className="text-xs opacity-60">({skill.proficiency})</span>
          {!readonly && onRemove && (
            <button onClick={() => onRemove(skill.id)} className="ml-0.5 hover:text-danger-500">
              <X className="h-3 w-3" />
            </button>
          )}
        </span>
      ))}
    </div>
  );
}
