interface SourceItem {
  source: string;
  count: number;
  interview_count: number;
  success_rate?: number;
}

interface Props {
  data: SourceItem[];
}

export default function SourceBreakdown({ data }: Props) {
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-gray-400">No source data available</p>;
  }

  return (
    <div className="space-y-3">
      {data.map((item) => (
        <div key={item.source} className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3">
          <div>
            <p className="text-sm font-medium text-gray-900">{item.source}</p>
            <p className="text-xs text-gray-500">{item.count} applications</p>
          </div>
          <div className="text-right">
            {item.interview_count > 0 && (
              <p className="text-sm font-medium text-green-600">
                {item.interview_count} interviews
              </p>
            )}
            {item.success_rate !== null && item.success_rate !== undefined && (
              <p className="text-xs text-gray-400">{item.success_rate.toFixed(0)}% success</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
