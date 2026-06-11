import { Search } from "lucide-react";

interface Props {
  query: string;
  onQueryChange: (q: string) => void;
  locationType: string;
  onLocationTypeChange: (v: string) => void;
  employmentType: string;
  onEmploymentTypeChange: (v: string) => void;
}

export default function JobFilters({
  query,
  onQueryChange,
  locationType,
  onLocationTypeChange,
  employmentType,
  onEmploymentTypeChange,
}: Props) {
  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search jobs..."
          className="block w-full rounded-lg border border-gray-300 py-2 pl-10 pr-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <select
          value={locationType}
          onChange={(e) => onLocationTypeChange(e.target.value)}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">All Locations</option>
          <option value="remote">Remote</option>
          <option value="hybrid">Hybrid</option>
          <option value="onsite">On-site</option>
        </select>
        <select
          value={employmentType}
          onChange={(e) => onEmploymentTypeChange(e.target.value)}
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">All Types</option>
          <option value="full-time">Full-time</option>
          <option value="part-time">Part-time</option>
          <option value="contract">Contract</option>
        </select>
      </div>
    </div>
  );
}
