import axios from "axios";
import type { ApiResponse, PaginatedResponse } from "../types";

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

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Request interceptor: attach auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401 with token refresh queue
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    // Only attempt refresh on 401, and only once per request
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

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
  },
);

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
