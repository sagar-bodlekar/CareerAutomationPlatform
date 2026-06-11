import type { Experience } from "../../types";
import { Briefcase } from "lucide-react";

interface Props {
  experiences: Experience[];
}

export default function ExperienceTimeline({ experiences }: Props) {
  return (
    <div className="space-y-6">
      {experiences.map((exp, i) => (
        <div key={exp.id || i} className="relative flex gap-4">
          {i < experiences.length - 1 && <div className="absolute left-4 top-10 h-full w-0.5 bg-gray-200" />}
          <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-100 text-primary-600">
            <Briefcase className="h-4 w-4" />
          </div>
          <div className="flex-1 pb-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-gray-900">{exp.title}</p>
                <p className="text-sm text-gray-500">{exp.company_name}</p>
              </div>
              {exp.is_current && (
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">Current</span>
              )}
            </div>
            <p className="mt-1 text-xs text-gray-400">
              {exp.start_date} – {exp.end_date || "Present"}
            </p>
            <p className="mt-1 text-sm text-gray-600">{exp.description}</p>
            {exp.technologies && exp.technologies.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {exp.technologies.map((tech) => (
                  <span key={tech} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{tech}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
