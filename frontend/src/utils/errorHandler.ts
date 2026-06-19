import type { AxiosError } from "axios";

export interface ParsedError {
  message: string;
  code: string;
  status: number;
  retryable: boolean;
}

export function getErrorMessage(error: unknown): string {
  const parsed = parseError(error);
  return parsed.message;
}

export function isNetworkError(error: unknown): boolean {
  if (error && typeof error === "object" && "code" in error) {
    return (error as { code: string }).code === "ERR_NETWORK";
  }
  return false;
}

export function isRetryable(error: unknown): boolean {
  return parseError(error).retryable;
}

export function parseError(error: unknown): ParsedError {
  const axiosError = error as AxiosError<{
    detail?: string;
    errors?: Array<{ message: string; code?: string }>;
    message?: string;
  }>;

  if (!axiosError || !axiosError.isAxiosError) {
    // Non-HTTP error (e.g., runtime exception)
    return {
      message: "An unexpected error occurred. Please try again.",
      code: "UNKNOWN",
      status: 0,
      retryable: false,
    };
  }

  const status = axiosError.response?.status ?? 0;
  const data = axiosError.response?.data;

  // Extract the best error message from the response
  let message = "An unexpected error occurred. Please try again.";
  if (data?.detail) {
    message = data.detail;
  } else if (data?.errors?.[0]?.message) {
    message = data.errors[0].message;
  } else if (data?.message) {
    message = data.message;
  } else if (axiosError.message) {
    message = axiosError.message;
  }

  // Determine if retryable
  const retryable = [429, 500, 502, 503, 504].includes(status) || isNetworkError(error);

  // Map status codes to user-friendly messages
  const statusMessages: Record<number, string> = {
    400: "Please check your input and try again.",
    401: "Your session has expired. Please log in again.",
    403: "You don't have permission to perform this action.",
    404: "The requested resource was not found.",
    409: "This resource already exists.",
    422: "Please fix the highlighted fields.",
    429: "Too many requests. Please wait a moment and try again.",
    500: "Something went wrong on our end. Please try again.",
    502: "Service temporarily unavailable. Please try again.",
    503: "Service is temporarily unavailable. Please try again later.",
    504: "The request is taking longer than expected. Please try again.",
  };

  // Use the status-specific message as the primary one unless we have a more specific detail
  const statusMessage = statusMessages[status];
  if (statusMessage && !data?.detail && !data?.errors?.[0]?.message) {
    message = statusMessage;
  }

  return {
    message,
    code: data?.errors?.[0]?.code ?? `HTTP_${status}`,
    status,
    retryable,
  };
}

export function isNotFoundError(error: unknown): boolean {
  return parseError(error).status === 404;
}

export function getFieldError(
  error: unknown,
  fieldName: string,
): string | undefined {
  const axiosError = error as AxiosError<{
    errors?: Array<{ field?: string; message: string }>;
  }>;
  if (!axiosError?.response?.data?.errors) return undefined;

  return axiosError.response.data.errors.find(
    (e) => e.field === fieldName,
  )?.message;
}
