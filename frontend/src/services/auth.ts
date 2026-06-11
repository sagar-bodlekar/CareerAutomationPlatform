import api, { createItem } from "./api";
import type { AuthTokens } from "../types";

export async function login(email: string, password: string): Promise<AuthTokens> {
  return createItem("/auth/login", { email, password });
}

export async function register(
  email: string,
  password: string,
  fullName: string,
): Promise<AuthTokens> {
  return createItem("/auth/register", { email, password, full_name: fullName });
}

export async function refreshToken(token: string): Promise<AuthTokens> {
  return createItem("/auth/refresh", { refresh_token: token });
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } catch {
    // Ignore errors on logout
  }
}

export async function getProfile() {
  const { data } = await api.get("/auth/me");
  return data.data;
}
