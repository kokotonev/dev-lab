import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { apiFetch } from "../lib/api";

interface User {
    id: number;
    email: string;
    username: string | null;
}

interface AuthContextValue {
    user: User | null;
    isLoading: boolean;
    setUser: (user: User | null) => void;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        apiFetch("/auth/status")
            .then(setUser)
            .catch(() => setUser(null))
            .finally(() => setIsLoading(false));
    }, []);

    async function logout() {
        await apiFetch("/auth/logout", { method: "POST" }).catch(() => {});
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, isLoading, setUser, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}
