import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { apiFetch } from "../lib/api"
import { useAuth } from "../context/AuthContext"

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();
    const { setUserId } = useAuth();

    async function handleSubmit(e: { preventDefault(): void }) {
        e.preventDefault();
        setError(null);

        try {
            await apiFetch("/auth/login", {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });
            const data = await apiFetch("/auth/status");
            setUserId(data.user_id);
            navigate("/dashboard");
        } catch (err) {
            setError((err as Error).message);
        }
    }

    return (
        <div className="max-w-sm mx-auto">
            <h2 className="mb-6 text-2xl text-center">Login Page</h2>
            <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <button type="submit" className="mt-3">
                    Login
                </button>
            </form>
        </div>
    )
}
