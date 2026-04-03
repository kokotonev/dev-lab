import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";

export default function RegisterPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirm, setConfirm] = useState("");
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    async function handleSubmit(e: { preventDefault(): void }) {
        e.preventDefault();
        setError(null);

        if (password !== confirm) {
            setError("Passwords do not match");
            return;
        }

        try {
            await apiFetch("/auth/register_user", {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });
            navigate("/login");
        } catch (err) {
            setError((err as Error).message);
        }
    }

    return (
        <div className="max-w-sm mx-auto">
            <h2 className="mb-6 text-2xl text-center">Register Page</h2>
            <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
                <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
                <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
                <input type="password" placeholder="Confirm Password" value={confirm} onChange={e => setConfirm(e.target.value)} required />
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <button type="submit" className="mt-3">Register</button>
            </form>
        </div>
    );
}
