import axios from "axios";
import type { ApiResponse, PaginatedResponse } from "../types";

// Extend InternalAxiosRequestConfig to include custom meta property
declare module "axios" {
  interface InternalAxiosRequestConfig {
    meta?: {
      requestStartedAt?: number;
    };
    _retryCount?: number;
    _retry?: boolean;
  }
}

// ── Configuration ────────────────────────────────────────

const DEFAULT_TIMEOUT = 30_000;         // 30s default
const UPLOAD_TIMEOUT = 120_000;         // 120s for file uploads
const MAX_RETRIES = 2;                  // Retry count for network failures

// ── Token refresh queue ──────────────────────────────────
// Prevents multiple simultaneous refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
}

async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) throw new Error("No refresh token");

  const { data } = await axios.post("/api/v1/auth/refresh", {
    refresh_token: refreshToken,
  });
  const { access_token, refresh_token: newRefreshToken } = data.data;
  localStorage.setItem("access_token", access_token);
  if (newRefreshToken) {
    localStorage.setItem("refresh_token", newRefreshToken);
  }
  return access_token;
}

// ── Correlation ID generation ────────────────────────────

function generateCorrelationId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `${timestamp}-${random}`;
}

// ── Retry-able status codes ──────────────────────────────

const RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504];

function isRetryableError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false;
  // Network failures (no response received)
  if (!error.response) return true;
  // Server-side retryable status codes
  return RETRYABLE_STATUS_CODES.includes(error.response.status);
}

// ── Axios instance ───────────────────────────────────────

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: DEFAULT_TIMEOUT,
});

// ── Request interceptor: attach auth token + correlation ID ──

api.interceptors.request.use((config) => {
  // Auth token
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Correlation ID for request tracing
  if (!config.headers["X-Request-ID"]) {
    config.headers["X-Request-ID"] = generateCorrelationId();
  }

  // Timeout: use upload timeout for POST/PUT requests with FormData
  if (config.data instanceof FormData) {
    config.timeout = UPLOAD_TIMEOUT;
  }

  return config;
});

// ── Response interceptor: auth refresh + retry + error logging ──

api.interceptors.response.use(
  (response) => {
    // Log slow responses in development
    if (import.meta.env.DEV && response.config.meta?.requestStartedAt) {
      const elapsed = Date.now() - response.config.meta.requestStartedAt;
      if (elapsed > 1000) {
        console.warn(
          `[API Slow] ${response.config.method?.toUpperCase()} ${response.config.url} — ${elapsed}ms`,
        );
      }
    }
    return response;
  },
  async (error) => {
    // Skip if we already handled this in a retry attempt
    const original = error.config;
    if (!original) return Promise.reject(error);

    // Log all API errors in development
    if (import.meta.env.DEV) {
      const method = original.method?.toUpperCase() ?? "?";
      const url = original.url ?? "?";
      const status = error.response?.status ?? "NETWORK_ERROR";
      const correlationId = original.headers?.["X-Request-ID"] ?? "?";
      console.error(
        `[API Error] ${method} ${url} → ${status} (X-Request-ID: ${correlationId})`,
        error.response?.data ?? error.message,
      );
    }

    // ── Retry logic for network failures & retryable status codes ──
    if (isRetryableError(error) && !original._retryCount) {
      original._retryCount = 0;
    }

    if (
      isRetryableError(error) &&
      original._retryCount !== undefined &&
      original._retryCount < MAX_RETRIES
    ) {
      original._retryCount += 1;
      // Exponential backoff: 1s, 2s
      const delay = original._retryCount * 1000;
      if (import.meta.env.DEV) {
        console.info(
          `[API Retry] ${original.method?.toUpperCase()} ${original.url} — attempt ${original._retryCount}/${MAX_RETRIES} after ${delay}ms`,
        );
      }
      await new Promise((resolve) => setTimeout(resolve, delay));
      return api(original);
    }

    // ── 401 handling with token refresh queue (only once per request) ──
    if (error.response?.status === 401 && !original._retry) {
      // If a refresh is already in progress, queue this request
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            return api(original);
          })
          .catch((err) => Promise.reject(err));
      }

      original._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        processQueue(null, newToken);
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

// ── Track request start time for slow request logging ──
api.interceptors.request.use((config) => {
  config.meta = config.meta ?? {};
  config.meta.requestStartedAt = Date.now();
  return config;
});

export default api;

export async function getList<T>(
  url: string,
  params?: Record<string, unknown>,
): Promise<PaginatedResponse<T>> {
  const { data } = await api.get<ApiResponse<{ items?: T[]; total?: number; page?: number; per_page?: number }> | { success: boolean; data: T[]; meta: { page: number; per_page: number; total: number; total_pages: number }; errors: null }>(url, { params });

  // Handle ApiResponse format: data.data = { items: [...], total: N } or { applications: [...], total: N }
  if ("data" in data) {
    const d = (data as any).data;
    if (d && typeof d === "object") {
      if (Array.isArray(d)) {
        // Direct array in data.data — PaginatedResponse<JobResponse>
        // The PaginatedResponse has meta, not nested in ApiResponse
        return {
          data: d,
          meta: { page: 1, per_page: 20, total: d.length },
        };
      }
      return {
        data: (d as any).items ?? (d as any).applications ?? [],
        meta: { page: (d as any).page ?? 1, per_page: (d as any).per_page ?? 20, total: (d as any).total ?? 0 },
      };
    }
    // data is an array — this is PaginatedResponse where data.data = the array directly
    // and data.meta has pagination info
    return {
      data: d,
      meta: { page: 1, per_page: 20, total: Array.isArray(d) ? d.length : 0 },
    };
  }

  // Handle PaginatedResponse format: { success: true, data: [...], meta: {...} }
  if ("success" in data) {
    const paginated = data as { success: boolean; data: T[]; meta: { page: number; per_page: number; total: number; total_pages: number } };
    return {
      data: paginated.data ?? [],
      meta: { page: paginated.meta?.page ?? 1, per_page: paginated.meta?.per_page ?? 20, total: paginated.meta?.total ?? 0 },
    };
  }

  return {
    data: [],
    meta: { page: 1, per_page: 20, total: 0 },
  };
}

export async function getById<T>(url: string): Promise<T> {
  const { data } = await api.get<ApiResponse<T>>(url);
  return data.data;
}

export async function createItem<T, R = T>(url: string, body: T): Promise<R> {
  const { data } = await api.post<ApiResponse<R>>(url, body);
  return data.data;
}

export async function updateItem<T, R = T>(url: string, body: Partial<T>): Promise<R> {
  const { data } = await api.put<ApiResponse<R>>(url, body);
  return data.data;
}

export async function postAction<R = unknown>(url: string, body?: unknown): Promise<R> {
  const { data } = await api.post<ApiResponse<R>>(url, body);
  return data.data;
}

export async function deleteItem<T = void>(url: string): Promise<T> {
  const { data } = await api.delete<ApiResponse<T>>(url);
  return data.data;
}
