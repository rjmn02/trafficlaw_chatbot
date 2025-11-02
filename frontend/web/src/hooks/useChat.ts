import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';
import { generateUUID } from '../utils/uuid';
import { API_BASE_URL } from '../constants';

export function useChat(sessionIdRef: React.MutableRefObject<string>) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const typingTimerRef = useRef<number | null>(null);
  const lastQueryRef = useRef<string>("");
  const endRef = useRef<HTMLDivElement | null>(null);
  const composerRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-scroll to the bottom when messages update
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Autosize composer
  useEffect(() => {
    const el = composerRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const max = 6 * 24; // ~6 lines
    el.style.height = Math.min(el.scrollHeight, max) + 'px';
  }, [query]);

  const typeMessage = (text: string) => {
    let revealed = "";
    setIsTyping(true);
    const step = () => {
      const chunk = text.slice(revealed.length, revealed.length + 6);
      revealed += chunk;
      setMessages(prev => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: "assistant", content: revealed };
        return copy;
      });
      if (revealed.length < text.length) {
        typingTimerRef.current = window.setTimeout(step, 12);
      } else { 
        setIsTyping(false); 
      }
    };
    step();
  };

  const onAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Client-side validation
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setErrorMessage("Please enter a question.");
      return;
    }
    
    // Enforce maximum query length (matching backend limit)
    const MAX_QUERY_LENGTH = 5000;
    if (trimmedQuery.length > MAX_QUERY_LENGTH) {
      setErrorMessage(`Query is too long. Maximum length is ${MAX_QUERY_LENGTH} characters.`);
      return;
    }
    
    setLoading(true);
    setErrorMessage("");
    lastQueryRef.current = trimmedQuery;
    
    if (!sessionIdRef.current) {
      sessionIdRef.current = generateUUID();
    }
    
    try {
      const userMsg: ChatMessage = { role: "user", content: trimmedQuery };
      setMessages(prev => [...prev, userMsg]);

      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionIdRef.current, query: trimmedQuery }),
      });
      
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `API error: ${res.status}`);
      }
      
      const data = await res.json();
      const answerText = data?.answer ?? "";
      
      // Progressive typing: append assistant message gradually
      const assistantMsg: ChatMessage = { role: "assistant", content: "" };
      setMessages(prev => [...prev, assistantMsg]);
      typeMessage(answerText);
      setQuery("");
    } catch (err) {
      // Handle validation errors from backend
      if (err instanceof Error && err.message.includes('validation')) {
        setErrorMessage("Invalid input. Please check your query and try again.");
      } else {
        setErrorMessage("Request failed. Please check the API server and your network.");
      }
    } finally {
      setLoading(false);
    }
  };

  const regenerateLast = async () => {
    if (loading) return;
    const lastUser = [...messages].reverse().find(m => m.role === 'user');
    if (!lastUser) return;
    
    setLoading(true);
    setErrorMessage("");
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionIdRef.current || generateUUID(), query: lastUser.content }),
      });
      
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `API error: ${res.status}`);
      }
      
      const data = await res.json();
      const answerText = data?.answer ?? "";
      
      // Replace content of the last assistant bubble
      setMessages(prev => {
        const copy = [...prev];
        const idx = copy.length - 1;
        if (copy[idx] && copy[idx].role === 'assistant') {
          copy[idx] = { role: 'assistant', content: "" };
        } else {
          copy.push({ role: 'assistant', content: "" });
        }
        return copy;
      });
      
      typeMessage(answerText);
    } catch (e) {
      setErrorMessage("Failed to regenerate. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (typingTimerRef.current) window.clearTimeout(typingTimerRef.current);
    };
  }, []);

  return {
    query,
    setQuery,
    messages,
    setMessages,
    errorMessage,
    setErrorMessage,
    loading,
    isTyping,
    lastQueryRef,
    endRef,
    composerRef,
    onAsk,
    regenerateLast,
  };
}

