import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { auth } from "../api/endpoints";
import type { User } from "../types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string, remember_me?: boolean) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      auth.me()
        .then((res) => { if (res.data.data) setUser(res.data.data); })
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string, remember_me?: boolean) => {
    const { data } = await auth.login({ email, password, remember_me });
    const d = data.data!;
    localStorage.setItem("access_token", d.access_token);
    localStorage.setItem("refresh_token", d.refresh_token);
    setUser(d.user);
  };

  const register = async (data: any) => {
    await auth.register(data);
  };

  const logout = async () => {
    try {
      await auth.logout();
    } catch {
      // server logout is best-effort
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
