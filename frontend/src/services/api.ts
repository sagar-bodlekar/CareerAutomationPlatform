import axios from "axios";
import type { ApiResponse, PaginatedResponse } from "../types";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const { data } = await axios.post("/api/v1/auth/refresh", {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = data.data;
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);
          original.headers.Authorization = `Bearer ${access_token}`;
          return api(original);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  },
);

export default api;

export async function getList<T>(
  url: string,
  params?: Record<string, unknown>,
): Promise<PaginatedResponse<T>> {
  const { data } = await api.get<ApiResponse<{ items?: T[]; total?: number; page?: number; per_page?: number }>>(url, { params });
  const d = data.data;
  return {
    data: (d as any).items ?? (d as any).applications ?? [],
    meta: { page: (d as any).page ?? 1, per_page: (d as any).per_page ?? 20, total: (d as any).total ?? 0 },
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
  const { data } = await api.patch<ApiResponse<R>>(url, body);
  return data.data;
}

export async function postAction<R = unknown>(url: string, body?: unknown): Promise<R> {
  const { data } = await api.post<ApiResponse<R>>(url, body);
  return data.data;
}
