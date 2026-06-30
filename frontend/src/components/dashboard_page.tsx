import { useEffect, useRef, useState } from "react";
import { apiFetch } from "../lib/api";

interface ChatMessage {
    role: string; // "user" | "assistant"
    content: string;
}

export default function DashboardPage() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [isSending, setIsSending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const bottomRef = useRef<HTMLDivElement>(null);

    // Load the existing conversation on page load.
    useEffect(() => {
        apiFetch("/agent/get_conversation")
            .then((data) => setMessages(data.conversation_history ?? []))
            .catch((err) => setError((err as Error).message))
            .finally(() => setIsLoading(false));
    }, []);

    // Keep the latest message in view.
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isSending]);

    async function handleSend(e: { preventDefault(): void }) {
        e.preventDefault();
        const content = input.trim();
        if (!content || isSending) return;

        setError(null);
        setInput("");
        setIsSending(true);
        // Optimistically show the user's message.
        setMessages((prev) => [...prev, { role: "user", content }]);

        try {
            const data = await apiFetch("/agent/ask", {
                method: "POST",
                body: JSON.stringify({ message: content }),
            });
            if (data.response) {
                setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
            }
        } catch (err) {
            setError((err as Error).message);
            // Roll back the optimistic message and restore the input so the user can retry.
            setMessages((prev) => prev.slice(0, -1));
            setInput(content);
        } finally {
            setIsSending(false);
        }
    }

    async function handleClear() {
        setError(null);
        try {
            await apiFetch("/agent/clear_conversation", { method: "DELETE" });
            setMessages([]);
        } catch (err) {
            setError((err as Error).message);
        }
    }

    return (
        <div className="max-w-2xl mx-auto flex flex-col h-[75vh]">
            <div className="flex justify-between items-center mb-3">
                <h2>Chat</h2>
                <button
                    onClick={handleClear}
                    disabled={messages.length === 0 || isSending}
                    className="disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    Clear conversation
                </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-surface border border-border rounded-card p-4 flex flex-col gap-3">
                {isLoading ? (
                    <p className="text-text-muted">Loading…</p>
                ) : messages.length === 0 ? (
                    <p className="text-text-muted">No messages yet. Say something to get started.</p>
                ) : (
                    messages.map((msg, i) => (
                        <div
                            key={i}
                            className={`max-w-[80%] px-3 py-2 rounded-card whitespace-pre-wrap break-words ${
                                msg.role === "user"
                                    ? "self-end bg-primary text-text"
                                    : "self-start bg-background border border-border text-text"
                            }`}
                        >
                            {msg.content}
                        </div>
                    ))
                )}
                {isSending && <p className="self-start text-text-muted">Thinking…</p>}
                <div ref={bottomRef} />
            </div>

            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

            <form className="flex gap-2 mt-3" onSubmit={handleSend}>
                <input
                    className="flex-1"
                    type="text"
                    placeholder="Type a message…"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isSending}
                />
                <button type="submit" disabled={isSending || !input.trim()}>
                    Send
                </button>
            </form>
        </div>
    );
}
