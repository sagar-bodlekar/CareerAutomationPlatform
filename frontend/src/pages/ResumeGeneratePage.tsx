import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Sparkles, FileText } from "lucide-react";

const templates = [
  { id: 1, name: "Modern", description: "Clean, contemporary layout with accent colors", popular: true },
  { id: 2, name: "Classic", description: "Traditional two-column resume layout", popular: false },
  { id: 3, name: "Minimal", description: "ATS-optimized minimal design", popular: false },
  { id: 4, name: "Professional", description: "Standard professional format", popular: true },
];

export default function ResumeGeneratePage() {
  const navigate = useNavigate();
  const [targetRole, setTargetRole] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState(1);
  const [optimizeAts, setOptimizeAts] = useState(true);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!targetRole.trim()) return;
    setGenerating(true);
    await new Promise((r) => setTimeout(r, 2000));
    setGenerating(false);
    navigate("/resumes");
  };

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Generate Resume</h1>
          <p className="text-gray-500">Create a role-optimized resume from your master profile</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* Role */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Target Role</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700">Job Title</label>
              <input
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g., Senior Frontend Engineer"
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Template selection */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Choose Template</h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {templates.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setSelectedTemplate(t.id)}
                  className={`rounded-xl border-2 p-4 text-left transition-all ${
                    selectedTemplate === t.id
                      ? "border-primary-500 bg-primary-50 shadow-sm"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{t.name}</span>
                    {t.popular && <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">Popular</span>}
                  </div>
                  <p className="mt-1 text-xs text-gray-500">{t.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Options */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Options</h2>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={optimizeAts}
                onChange={(e) => setOptimizeAts(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">Enable ATS Optimization</p>
                <p className="text-xs text-gray-500">AI-powered keyword optimization for better ATS scores</p>
              </div>
            </label>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-semibold text-gray-900">Ready to generate?</h3>
            <p className="mb-4 text-sm text-gray-500">
              This will create a new resume optimized for "{targetRole || "your target role"}" using your profile data.
            </p>
            <button
              onClick={handleGenerate}
              disabled={!targetRole.trim() || generating}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Generate Resume
                </>
              )}
            </button>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-2 font-semibold text-gray-900">What to expect</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-primary-500" />
                <span>Tailored content for your target role</span>
              </li>
              <li className="flex items-start gap-2">
                <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary-500" />
                <span>ATS-optimized keywords and formatting</span>
              </li>
              <li className="flex items-start gap-2">
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-primary-500" />
                <span>Professional PDF output</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
