import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { login as apiLogin, register as apiRegister, logout as apiLogout, getProfile } from "../services/auth";
import type { User } from "../types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AUTH_SYNC_KEY = "auth_logout_event";

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Multi-tab session sync: listen for logout events from other tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === AUTH_SYNC_KEY) {
        // Another tab logged out
        setUser(null);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
      if (e.key === "access_token" && !e.newValue) {
        // Token was cleared in another tab
        setUser(null);
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      getProfile()
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await apiLogin(email, password);
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    const u = await getProfile();
    setUser(u);
  }, []);

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    const tokens = await apiRegister(email, password, fullName);
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    const u = await getProfile();
    setUser(u);
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    // Signal other tabs to logout
    try {
      localStorage.setItem(AUTH_SYNC_KEY, Date.now().toString());
      localStorage.removeItem(AUTH_SYNC_KEY);
    } catch { /* ignore if other tab already handled */ }
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
