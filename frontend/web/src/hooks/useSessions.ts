import { useState, useEffect } from 'react';
import { StoredSession, ChatMessage } from '../types';
import { generateUUID } from '../utils/uuid';
import { STORAGE_KEYS, API_BASE_URL } from '../constants';

export function useSessions(sessionIdRef: React.MutableRefObject<string>, messages: ChatMessage[], query: string, setQuery: (q: string) => void) {
  const [sessions, setSessions] = useState<StoredSession[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Load sessions from localStorage on mount
  // Sort by updatedAt only on initial load (most recent first)
  useEffect(() => {
    const raw = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEYS.sessions) : null;
    if (raw) {
      try {
        const parsed: StoredSession[] = JSON.parse(raw);
        // Sort by updatedAt descending (most recent first) only on initial load
        setSessions(parsed.sort((a,b)=>b.updatedAt-a.updatedAt));
      } catch {
        // Silently ignore corrupted localStorage data
      }
    }
  }, []);

  // Persist current session to localStorage whenever messages change
  useEffect(() => {
    if (!sessionIdRef.current || messages.length === 0) return;
    
    const title = messages.find(m => m.role === 'user')?.content?.slice(0, 40) || 'New chat';
    setSessions(prev => {
      const existingIdx = prev.findIndex(s => s.id === sessionIdRef.current);
      const existing = existingIdx >= 0 ? prev[existingIdx] : null;
      
      // Only update updatedAt if messages actually changed (new message added)
      const messagesChanged = !existing || existing.messages.length !== messages.length;
      const updatedAt = messagesChanged ? Date.now() : (existing?.updatedAt || Date.now());
      
      const updated: StoredSession = {
        id: sessionIdRef.current,
        title: existing?.title || title, // Preserve custom title if exists
        messages,
        updatedAt,
      };
      
      const next = existingIdx >= 0
        ? [...prev.slice(0, existingIdx), updated, ...prev.slice(existingIdx+1)]
        : [updated, ...prev];
      
      localStorage.setItem(STORAGE_KEYS.sessions, JSON.stringify(next));
      
      // Only sort by updatedAt on initial load, preserve order when switching chats
      return next;
    });
  }, [messages, sessionIdRef]);

  // Persist composer draft per session
  useEffect(() => {
    const sid = sessionIdRef.current || "";
    if (!sid) return;
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.draft(sid), query);
    }
  }, [query, sessionIdRef]);

  // Load composer draft when session changes
  useEffect(() => {
    const sid = sessionIdRef.current || "";
    if (!sid) return;
    if (typeof window !== 'undefined') {
      const draft = localStorage.getItem(STORAGE_KEYS.draft(sid)) || "";
      setQuery(draft);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionIdRef.current]);

  const switchToSession = (id: string): ChatMessage[] | undefined => {
    const found = sessions.find(s => s.id === id);
    if (!found) return undefined;
    sessionIdRef.current = id;
    return found.messages;
  };

  const deleteSession = (id: string): ChatMessage[] | null => {
    setSessions(prev => {
      const next = prev.filter(s => s.id !== id);
      localStorage.setItem(STORAGE_KEYS.sessions, JSON.stringify(next));
      return next;
    });
    if (sessionIdRef.current === id) {
      sessionIdRef.current = "";
      return [];
    }
    return null;
  };

  const onNewChat = async (): Promise<ChatMessage[]> => {
    try {
      // best-effort clear of existing session on the server
      if (sessionIdRef.current) {
        await fetch(`${API_BASE_URL}/api/sessions/${sessionIdRef.current}`, { method: "DELETE" }).catch(() => {});
      }
      sessionIdRef.current = generateUUID();
      return [];
    } catch {
      return [];
    }
  };

  const renameSession = (id: string, newTitle: string): void => {
    const trimmedTitle = newTitle.trim().slice(0, 50) || 'Untitled';
    setSessions(prev => {
      const next = prev.map(s => 
        s.id === id ? { ...s, title: trimmedTitle } : s
      );
      localStorage.setItem(STORAGE_KEYS.sessions, JSON.stringify(next));
      return next;
    });
  };

  const filteredSessions = sessions.filter(s => 
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return {
    sessions,
    setSessions,
    searchQuery,
    setSearchQuery,
    filteredSessions,
    switchToSession,
    deleteSession,
    onNewChat,
    renameSession,
  };
}

