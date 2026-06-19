import { useIsMutating } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";

export default function SavingIndicator() {
  const isMutating = useIsMutating();

  if (!isMutating) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-full bg-primary-600 px-4 py-2 text-xs font-medium text-white shadow-lg animate-fade-in">
      <Loader2 className="h-3.5 w-3.5 animate-spin" />
      Saving...
    </div>
  );
}
