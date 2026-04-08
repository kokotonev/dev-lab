import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { apiFetch } from "../lib/api";

interface AuthContextValue {
    userId: string | null;
    isLoading: boolean;
    setUserId: (userId: string | null) => void;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [userId, setUserId] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        apiFetch("/auth/status")
            .then((data) => setUserId(data.user_id))
            .catch(() => setUserId(null))
            .finally(() => setIsLoading(false));
    }, []);

    async function logout() {
        await apiFetch("/auth/logout", { method: "POST" }).catch(() => {});
        setUserId(null);
    }

    return (
        <AuthContext.Provider value={{ userId, isLoading, setUserId, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}
