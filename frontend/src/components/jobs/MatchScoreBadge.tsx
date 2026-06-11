interface Props {
  score: number;
  size?: "sm" | "md";
}

export default function MatchScoreBadge({ score, size = "sm" }: Props) {
  const color = score >= 85 ? "bg-green-100 text-green-700" : score >= 70 ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700";
  const px = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";

  return <span className={`inline-flex items-center rounded-full font-semibold ${color} ${px}`}>{score}%</span>;
}
