import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

export interface Toast {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  duration?: number; // ms, default success=3000, error=8000
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => string;
  removeToast: (id: string) => void;
  success: (message: string, action?: Toast["action"]) => string;
  error: (message: string, action?: Toast["action"]) => string;
  info: (message: string, action?: Toast["action"]) => string;
  warning: (message: string, action?: Toast["action"]) => string;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let toastCounter = 0;

function generateId(): string {
  toastCounter += 1;
  return `toast-${toastCounter}-${Date.now()}`;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(
    (toast: Omit<Toast, "id">): string => {
      const id = generateId();
      const duration = toast.duration ?? (toast.type === "error" ? 8000 : 3000);
      const newToast: Toast = { ...toast, id, duration };

      setToasts((prev) => [...prev, newToast]);

      // Auto-dismiss
      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }

      return id;
    },
    [removeToast],
  );

  const success = useCallback(
    (message: string, action?: Toast["action"]) =>
      addToast({ type: "success", message, action }),
    [addToast],
  );

  const error = useCallback(
    (message: string, action?: Toast["action"]) =>
      addToast({ type: "error", message, action }),
    [addToast],
  );

  const info = useCallback(
    (message: string, action?: Toast["action"]) =>
      addToast({ type: "info", message, action }),
    [addToast],
  );

  const warning = useCallback(
    (message: string, action?: Toast["action"]) =>
      addToast({ type: "warning", message, action }),
    [addToast],
  );

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, success, error, info, warning }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return ctx;
}
