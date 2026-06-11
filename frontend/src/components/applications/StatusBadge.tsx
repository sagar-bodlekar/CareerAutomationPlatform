interface Props {
  status: string;
  size?: "sm" | "md";
}

const statusConfig: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-gray-100 text-gray-700" },
  matched: { label: "Matched", color: "bg-blue-100 text-blue-700" },
  resume_generated: { label: "Resume Ready", color: "bg-indigo-100 text-indigo-700" },
  cover_letter_generated: { label: "Letter Ready", color: "bg-purple-100 text-purple-700" },
  email_prepared: { label: "Email Ready", color: "bg-pink-100 text-pink-700" },
  sent: { label: "Sent", color: "bg-cyan-100 text-cyan-700" },
  delivered: { label: "Delivered", color: "bg-teal-100 text-teal-700" },
  opened: { label: "Opened", color: "bg-emerald-100 text-emerald-700" },
  replied: { label: "Replied", color: "bg-green-100 text-green-700" },
  interview_scheduled: { label: "Interview", color: "bg-lime-100 text-lime-700" },
  offer_received: { label: "Offer!", color: "bg-amber-100 text-amber-700" },
  rejected: { label: "Rejected", color: "bg-red-100 text-red-700" },
  withdrawn: { label: "Withdrawn", color: "bg-gray-200 text-gray-500" },
};

export default function StatusBadge({ status, size = "sm" }: Props) {
  const cfg = statusConfig[status] || { label: status, color: "bg-gray-100 text-gray-700" };
  const px = size === "sm" ? "px-2.5 py-0.5 text-xs" : "px-3 py-1 text-sm";

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${cfg.color} ${px}`}>
      {cfg.label}
    </span>
  );
}
