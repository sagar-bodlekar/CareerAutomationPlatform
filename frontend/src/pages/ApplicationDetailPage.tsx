import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Send, Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";

const mockApp = {
  id: 1,
  company: "Tech Corp",
  role: "Senior Software Engineer",
  status: "interview_scheduled",
  progress: 85,
  matchScore: 92,
  created: "Jan 15, 2026",
  sent: "Jan 16, 2026",
  delivered: "Jan 17, 2026",
  opened: "Jan 18, 2026",
  replied: "Jan 20, 2026",
  interview: "Jan 28, 2026",
  events: [
    { status: "draft", label: "Draft Created", date: "Jan 15", description: "Application draft created", completed: true },
    { status: "sent", label: "Application Sent", date: "Jan 16", description: "Email sent with resume and cover letter", completed: true },
    { status: "delivered", label: "Delivered", date: "Jan 17", description: "Email delivered successfully", completed: true },
    { status: "opened", label: "Opened by Recipient", date: "Jan 18", description: "Recipient opened the email", completed: true },
    { status: "replied", label: "Replied", date: "Jan 20", description: "Recipient replied expressing interest", completed: true },
    { status: "interview_scheduled", label: "Interview Scheduled", date: "Jan 28", description: "Technical interview scheduled", completed: true, isCurrent: true },
    { status: "offer_received", label: "Offer Received", date: "Pending", description: "Awaiting decision after interview", completed: false },
  ],
};

const statusIcons: Record<string, React.ElementType> = {
  draft: Clock,
  sent: Send,
  delivered: CheckCircle2,
  opened: CheckCircle2,
  replied: CheckCircle2,
  interview_scheduled: Clock,
  offer_received: Loader2,
  rejected: XCircle,
  withdrawn: XCircle,
};

export default function ApplicationDetailPage() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 1500));
    setSubmitting(false);
  };

  return (
    <div className="animate-fade-in space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to applications
      </button>

      {/* Header */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{mockApp.role}</h1>
            <p className="text-lg text-gray-500">{mockApp.company}</p>
            <p className="mt-1 text-sm text-gray-400">Created {mockApp.created}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-center">
              <span className="text-lg font-bold text-green-600">{mockApp.matchScore}%</span>
              <span className="text-xs text-gray-400">Match</span>
            </div>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-50"
            >
              {submitting ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Submit Application
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Timeline */}
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-gray-900">Application Timeline</h2>
          <div className="relative">
            {mockApp.events.map((event, i) => {
              const Icon = statusIcons[event.status] || Clock;
              const isLast = i === mockApp.events.length - 1;

              return (
                <div key={i} className="relative flex gap-4 pb-8 last:pb-0">
                  {!isLast && <div className="absolute left-4 top-8 h-full w-0.5 bg-gray-200" />}
                  <div
                    className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                      event.completed ? "bg-green-100 text-green-600" : event.isCurrent ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-400"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className={`text-sm font-medium ${event.completed ? "text-gray-900" : event.isCurrent ? "text-blue-700" : "text-gray-400"}`}>
                          {event.label}
                        </p>
                        <p className="text-xs text-gray-500">{event.description}</p>
                      </div>
                      <span className="text-xs text-gray-400">{event.date}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Package info */}
        <div className="space-y-4">
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Application Package</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <span className="text-sm text-gray-700">Resume</span>
                <span className="text-sm font-medium text-green-600">Attached</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <span className="text-sm text-gray-700">Cover Letter</span>
                <span className="text-sm font-medium text-green-600">Generated</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <span className="text-sm text-gray-700">Email</span>
                <span className="text-sm font-medium text-green-600">Prepared</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <span className="text-sm text-gray-700">ATS Score</span>
                <span className="text-sm font-semibold text-green-600">91%</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Status Details</h2>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Current Status</dt>
                <dd className="font-medium text-blue-700">Interview Scheduled</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Progress</dt>
                <dd className="font-medium text-gray-900">85%</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Retry Count</dt>
                <dd className="font-medium text-gray-900">0</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Delivery Status</dt>
                <dd className="font-medium text-green-600">Delivered</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
