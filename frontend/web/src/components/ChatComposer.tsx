import React from 'react';
import { COLORS } from '../constants';

interface ChatComposerProps {
  query: string;
  setQuery: (q: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  composerRef: React.RefObject<HTMLTextAreaElement | null>;
}

export function ChatComposer({ query, setQuery, onSubmit, loading, composerRef }: ChatComposerProps) {
  return (
    <form onSubmit={onSubmit} className="mt-4 w-full max-w-5xl flex gap-2 relative">
      <textarea
        ref={composerRef}
        rows={1}
        className="flex-1 border-2 rounded-lg px-4 pr-28 py-3 text-base resize-none focus:outline-none focus:ring-2 shadow-md"
        style={{
          borderColor: COLORS.accent,
          backgroundColor: '#ffffff',
          color: COLORS.dark,
        }}
        placeholder="Ask about Philippine traffic laws..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!loading) onSubmit(e as unknown as React.FormEvent);
          }
        }}
        disabled={loading}
      />
      <button
        className="absolute right-2 top-1/2 -translate-y-1/2 text-white px-4 py-2 rounded-lg cursor-pointer shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 transition-all font-medium"
        style={{ backgroundColor: COLORS.primary }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.accent; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary; }}
        disabled={loading}
      >
        {loading ? "Asking…" : "Ask"}
      </button>
    </form>
  );
}

