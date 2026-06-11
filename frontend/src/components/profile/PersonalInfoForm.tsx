import type { PersonalInfo } from "../../types";

interface Props {
  data?: PersonalInfo;
  onChange?: (data: Partial<PersonalInfo>) => void;
}

export default function PersonalInfoForm({ data, onChange }: Props) {
  const handleChange = (field: string, value: string) => {
    onChange?.({ [field]: value } as Partial<PersonalInfo>);
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <label className="block text-sm font-medium text-gray-700">Full name</label>
        <input
          type="text"
          defaultValue={data?.full_name}
          onChange={(e) => handleChange("full_name", e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Email</label>
        <input
          type="email"
          defaultValue={data?.email}
          onChange={(e) => handleChange("email", e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Phone</label>
        <input
          type="tel"
          defaultValue={data?.phone}
          onChange={(e) => handleChange("phone", e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Location</label>
        <input
          type="text"
          defaultValue={data?.location}
          onChange={(e) => handleChange("location", e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">LinkedIn URL</label>
        <input
          type="url"
          defaultValue={data?.linkedin_url}
          onChange={(e) => handleChange("linkedin_url", e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">GitHub URL</label>
        <input
          type="url"
          defaultValue={data?.github_url}
          onChange={(e) => handleChange("github_url", e.target.value)}
          className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>
    </div>
  );
}
