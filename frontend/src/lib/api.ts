const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function apiFetch(path: string, options?: RequestInit) {
    const response = await fetch(`${BASE_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        ...options,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail ?? "Request failed");
    }

    return response.json();
}
