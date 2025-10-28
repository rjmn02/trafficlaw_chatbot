"use client";
import { useRef, useState } from "react";

// Simple UUID generator that works everywhere
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef<string>("");

  const onAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    
    // Generate session ID only on client side
    if (!sessionIdRef.current) {
      sessionIdRef.current = generateUUID();
    }
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionIdRef.current, query }),
      });
      const data = await res.json();
      setAnswer(data?.answer ?? "");
    } catch (err) {
      setAnswer("Request failed. Check API server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-2xl p-6 min-h-screen">
      <h1 className="text-2xl font-semibold mb-4">TrafficLaw Chatbot</h1>
      <form onSubmit={onAsk} className="flex gap-2 mb-4">
        <input
          className="flex-1 border rounded px-3 py-2"
          placeholder="Ask about Philippine traffic laws..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="bg-black text-white px-4 py-2 rounded" disabled={loading}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>
      {answer && (
        <div className="prose whitespace-pre-wrap border rounded p-4">
          {answer}
        </div>
      )}
    </main>
  );
}
