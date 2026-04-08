const BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function doFetch(path: string, options?: RequestInit) {
    return fetch(`${BASE_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        ...options,
    });
}

// Singleton promise — prevents concurrent refresh attempts from racing
let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
    if (refreshPromise) return refreshPromise;

    refreshPromise = doFetch("/auth/refresh", { method: "POST" })
        .then(r => r.ok)
        .finally(() => { refreshPromise = null; });

    return refreshPromise;
}

export async function apiFetch(path: string, options?: RequestInit) {
    let response = await doFetch(path, options);

    // Access token expired — attempt a silent refresh then retry once
    if (response.status === 401 && path !== "/auth/refresh" && path !== "/auth/login") {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            response = await doFetch(path, options);
        } else {
            throw new Error("Session expired. Please log in again.");
        }
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail ?? "Request failed");
    }

    return response.json();
}
