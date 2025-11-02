"use client";
import React, { useEffect, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import { useSessions } from "../hooks/useSessions";
import { ChatMessage } from "../components/ChatMessage";
import { ChatComposer } from "../components/ChatComposer";
import { EmptyState } from "../components/EmptyState";
import { ErrorMessage } from "../components/ErrorMessage";
import { Sidebar } from "../components/Sidebar";
import { COLORS } from "../constants";

export default function Home() {
  const sessionIdRef = useRef<string>("");
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

  const {
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
  } = useChat(sessionIdRef);

  const {
    sessions,
    setSessions,
    searchQuery,
    setSearchQuery,
    filteredSessions,
    switchToSession,
    deleteSession,
    onNewChat,
  } = useSessions(sessionIdRef, messages, query, setQuery);


  // Load sessions and set up keyboard shortcut
  useEffect(() => {
    const onGlobalKey = (ev: KeyboardEvent) => {
      if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === 'k') {
        ev.preventDefault();
        composerRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onGlobalKey);
    return () => {
      window.removeEventListener('keydown', onGlobalKey);
    };
  }, [composerRef]);

  const handleSwitchSession = (id: string) => {
    const newMessages = switchToSession(id);
    if (newMessages) {
      setMessages(newMessages);
      setQuery("");
      setErrorMessage("");
    }
  };

  const handleDeleteSession = (id: string) => {
    const newMessages = deleteSession(id);
    if (newMessages !== null) {
      setMessages(newMessages);
      setQuery("");
    }
  };

  const handleNewChat = async () => {
    const newMessages = await onNewChat();
    setMessages(newMessages);
    setQuery("");
    setErrorMessage("");
  };

  const handleRetry = () => {
    if (!loading && lastQueryRef.current) {
      onAsk({ preventDefault: () => {} } as unknown as React.FormEvent);
    }
  };

  return (
    <main className="w-full h-screen flex relative overflow-hidden" style={{ backgroundColor: COLORS.background }}>
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black bg-opacity-30 z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <Sidebar
        sessions={sessions}
        filteredSessions={filteredSessions}
        currentSessionId={sessionIdRef.current}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        sidebarOpen={sidebarOpen}
        sidebarCollapsed={sidebarCollapsed}
        setSidebarCollapsed={setSidebarCollapsed}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
        onSwitchSession={handleSwitchSession}
        onDeleteSession={handleDeleteSession}
        loading={loading}
      />

      {/* Main column */}
      <section className="flex-1 flex flex-col h-screen overflow-hidden">
        <div className="w-full max-w-5xl mx-auto px-6 pt-6 pb-2 flex-shrink-0">
          <h1 className="text-2xl font-semibold" style={{ color: COLORS.dark }}>TrafficLaw Chatbot</h1>
        </div>

        {/* Messages list - scrollable */}
        <div className="flex-1 w-full max-w-5xl mx-auto px-6 overflow-y-auto space-y-4" aria-live="polite">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <EmptyState />
            </div>
          ) : (
            <>
              {messages.map((m, idx) => (
                <ChatMessage
                  key={idx}
                  message={m}
                  isLast={idx === messages.length - 1}
                  onRegenerate={regenerateLast}
                  loading={loading}
                />
              ))}
              {isTyping && (
                <div className="text-xs pl-1" style={{ color: COLORS.accent }}>Assistant is typing…</div>
              )}
              <div ref={endRef} />
            </>
          )}
        </div>

        {/* Fixed bottom section */}
        <div className="w-full max-w-5xl mx-auto px-6 pb-6 flex-shrink-0 space-y-3">
          {errorMessage && (
            <ErrorMessage
              message={errorMessage}
              onRetry={handleRetry}
              loading={loading}
            />
          )}

          <ChatComposer
            query={query}
            setQuery={setQuery}
            onSubmit={onAsk}
            loading={loading}
            composerRef={composerRef}
          />
        </div>
      </section>
    </main>
  );
}
