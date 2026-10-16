import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, tokenStore } from "./lib/api";
import type { User } from "./types";

type AuthValue = { user: User | null; ready: boolean; signIn: (email: string, password: string) => Promise<void>; signInWithGoogle: (idToken: string) => Promise<void>; verify: (email: string, code: string) => Promise<void>; signOut: () => Promise<void>; refreshUser: () => Promise<void> };
const AuthContext = createContext<AuthValue | null>(null);
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null); const [ready, setReady] = useState(false);
  const refreshUser = async () => { if (!tokenStore.hasAccess()) { setReady(true); return; } try { setUser(await api.me()); } catch { tokenStore.clear(); setUser(null); } finally { setReady(true); } };
  useEffect(() => { void refreshUser(); }, []);
  const value = useMemo(() => ({ user, ready, refreshUser, signIn: async (email: string, password: string) => { tokenStore.set(await api.login(email, password)); await refreshUser(); }, signInWithGoogle: async (idToken: string) => { tokenStore.set(await api.googleLogin(idToken)); await refreshUser(); }, verify: async (email: string, code: string) => { tokenStore.set(await api.verify(email, code)); await refreshUser(); }, signOut: async () => { try { await api.logout(); } finally { tokenStore.clear(); setUser(null); } } }), [user, ready]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error("AuthProvider is missing"); return value; }
