export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatRelativeDate(date: string | Date): string {
  const now = new Date();
  const d = new Date(date);
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return formatDate(date);
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const d = new Date(date);
  const diffMs = now.getTime() - d.getTime();
  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return "Just now";
  if (minutes === 1) return "1m ago";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours === 1) return "1h ago";
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  return formatDate(date);
}

export function formatSalary(min?: number, max?: number, currency = "USD"): string {
  const fmt = (n: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency, maximumFractionDigits: 0 }).format(n);

  if (min && max) return `${fmt(min)} - ${fmt(max)}`;
  if (min) return `From ${fmt(min)}`;
  if (max) return `Up to ${fmt(max)}`;
  return "Not specified";
}

export function getScoreColor(score: number): string {
  if (score >= 85) return "score-high";
  if (score >= 70) return "score-medium";
  return "score-low";
}

export function getScoreLabel(score: number): string {
  if (score >= 85) return "Excellent match";
  if (score >= 70) return "Good match";
  if (score >= 50) return "Fair match";
  return "Weak match";
}

export function capitalize(str: string): string {
  return str
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen).trimEnd() + "...";
}

export function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: "Draft",
    matched: "Matched to Job",
    resume_generated: "Resume Generated",
    cover_letter_generated: "Cover Letter Generated",
    email_prepared: "Email Prepared",
    sent: "Sent",
    delivered: "Delivered",
    opened: "Opened by Recipient",
    replied: "Replied",
    interview_scheduled: "Interview Scheduled",
    offer_received: "Offer Received",
    rejected: "Rejected",
    withdrawn: "Withdrawn",
  };
  return labels[status] || capitalize(status);
}
