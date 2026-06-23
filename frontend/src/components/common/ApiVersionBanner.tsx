import { useState, useEffect } from "react";
import { AlertTriangle, X } from "lucide-react";
import api from "../../services/api";

const EXPECTED_API_VERSION = "1.0";

export default function ApiVersionBanner() {
  const [apiVersion, setApiVersion] = useState<string | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Check API version via response interceptor header
    const interceptorId = api.interceptors.response.use(
      (response) => {
        const version = response.headers["x-api-version"];
        if (version) {
          setApiVersion(version);
        }
        return response;
      },
      (error) => {
        const version = error.response?.headers?.["x-api-version"];
        if (version) setApiVersion(version);
        return Promise.reject(error);
      },
    );

    return () => {
      api.interceptors.response.eject(interceptorId);
    };
  }, []);

  const isMismatch = apiVersion !== null && apiVersion !== EXPECTED_API_VERSION;

  if (dismissed || !isMismatch) return null;

  return (
    <div className="flex items-center justify-between bg-amber-50 px-4 py-2 text-xs text-amber-800 border-b border-amber-200">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
        <span>
          API version mismatch: expected <strong>{EXPECTED_API_VERSION}</strong>, received <strong>{apiVersion}</strong>.
          Some features may not work as expected.
        </span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="ml-4 shrink-0 rounded p-0.5 hover:bg-amber-100 transition-colors"
        aria-label="Dismiss"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
