import { useEffect, useState } from "react";
import { CheckCircle, XCircle, AlertTriangle, Info, X, RefreshCw } from "lucide-react";
import { useToast, type Toast as ToastType } from "../../context/ToastContext";

const typeConfig: Record<
  ToastType["type"],
  { icon: React.ElementType; bg: string; border: string; text: string; ring: string }
> = {
  success: {
    icon: CheckCircle,
    bg: "bg-green-50",
    border: "border-green-200",
    text: "text-green-800",
    ring: "ring-green-500",
  },
  error: {
    icon: XCircle,
    bg: "bg-red-50",
    border: "border-red-200",
    text: "text-red-800",
    ring: "ring-red-500",
  },
  warning: {
    icon: AlertTriangle,
    bg: "bg-amber-50",
    border: "border-amber-200",
    text: "text-amber-800",
    ring: "ring-amber-500",
  },
  info: {
    icon: Info,
    bg: "bg-blue-50",
    border: "border-blue-200",
    text: "text-blue-800",
    ring: "ring-blue-500",
  },
};

function ToastItem({ toast }: { toast: ToastType }) {
  const { removeToast } = useToast();
  const [isExiting, setIsExiting] = useState(false);
  const config = typeConfig[toast.type];

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => removeToast(toast.id), 200);
  };

  // Dismiss on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleDismiss();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [toast.id]);

  const Icon = config.icon;

  return (
    <div
      role="alert"
      className={`pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl border ${config.border} ${config.bg} p-4 shadow-lg ring-1 ${config.ring} ring-opacity-20 transition-all duration-200 ${
        isExiting ? "translate-x-full opacity-0" : "translate-x-0 opacity-100"
      }`}
    >
      <Icon className={`h-5 w-5 shrink-0 ${config.text}`} />
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${config.text}`}>{toast.message}</p>
        {toast.action && (
          <button
            onClick={() => {
              toast.action!.onClick();
              handleDismiss();
            }}
            className={`mt-1.5 inline-flex items-center gap-1 text-xs font-medium ${config.text} hover:underline`}
          >
            <RefreshCw className="h-3 w-3" />
            {toast.action.label}
          </button>
        )}
      </div>
      <button
        onClick={handleDismiss}
        className={`shrink-0 rounded-md p-1 transition-colors hover:bg-black/5 ${config.text}`}
        aria-label="Dismiss"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const { toasts } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div
      className="fixed bottom-4 right-4 z-[100] flex flex-col-reverse gap-2 pointer-events-none"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}
