import type { ResumeTemplate } from "../../types";

interface Props {
  templates: ResumeTemplate[];
  selectedId: number;
  onSelect: (id: number) => void;
}

export default function TemplateSelector({ templates, selectedId, onSelect }: Props) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {templates.map((t) => (
        <button
          key={t.id}
          onClick={() => onSelect(t.id)}
          className={`rounded-xl border-2 p-4 text-left transition-all ${
            selectedId === t.id
              ? "border-primary-500 bg-primary-50 shadow-sm"
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-medium text-gray-900">{t.name}</span>
            {t.is_default && <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">Default</span>}
          </div>
          {t.description && <p className="mt-1 text-xs text-gray-500">{t.description}</p>}
        </button>
      ))}
    </div>
  );
}
