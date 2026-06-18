import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorFallbackProps {
  message?: string;
  onRetry?: () => void;
  compact?: boolean;
}

export function ErrorFallback({ message, onRetry, compact = false }: ErrorFallbackProps) {
  if (compact) {
    return (
      <div className="flex items-center gap-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
        <AlertCircle className="h-4 w-4 shrink-0" />
        <span className="flex-1">{message || "Something went wrong."}</span>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-100 transition-colors"
          >
            <RefreshCw className="h-3 w-3" />
            Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-red-100 bg-red-50 p-8 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 mb-3">
        <AlertCircle className="h-6 w-6 text-red-500" />
      </div>
      <h3 className="text-base font-semibold text-red-800">Something went wrong</h3>
      <p className="mt-1 text-sm text-red-600 max-w-md">
        {message || "An unexpected error occurred. Please try again."}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      )}
    </div>
  );
}
