"use client";
import React, { useEffect, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import { useSessions } from "../hooks/useSessions";
import { ChatMessage } from "../components/ChatMessage";
import { ChatComposer } from "../components/ChatComposer";
import { EmptyState } from "../components/EmptyState";
import { ErrorMessage } from "../components/ErrorMessage";
import { Sidebar } from "../components/Sidebar";
import { TypingIndicator } from "../components/TypingIndicator";
import { ScrollToBottom } from "../components/ScrollToBottom";
import { MessageSkeleton } from "../components/MessageSkeleton";
import { ToastContainer } from "../components/Toast";
import { useToast } from "../hooks/useToast";
import { COLORS } from "../constants";

export default function Home() {
  const sessionIdRef = useRef<string>("");
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [showScrollButton, setShowScrollButton] = useState<boolean>(false);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const { toasts, showToast, removeToast } = useToast();

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
    stopTyping,
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
    renameSession,
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

  // Scroll detection for scroll-to-bottom button
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 200;
      setShowScrollButton(!isNearBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const handleScrollToBottom = () => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSwitchSession = (id: string) => {
    // Stop any ongoing typing animation when switching sessions
    stopTyping();
    const newMessages = switchToSession(id);
    if (newMessages) {
      setMessages(newMessages);
      setQuery("");
      setErrorMessage("");
    }
  };

  const handleDeleteSession = (id: string) => {
    // Stop any ongoing typing animation when deleting session
    stopTyping();
    const newMessages = deleteSession(id);
    // Always show toast when a chat is deleted
    showToast('Chat deleted', 'success');
    if (newMessages !== null) {
      setMessages(newMessages);
      setQuery("");
    }
  };

  const handleNewChat = async () => {
    // Stop any ongoing typing animation when starting new chat
    stopTyping();
    const newMessages = await onNewChat();
    setMessages(newMessages);
    setQuery("");
    setErrorMessage("");
  };

  const handleExampleClick = (question: string) => {
    setQuery(question);
    composerRef.current?.focus();
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    showToast('Copied to clipboard!', 'success');
  };

  const handleRenameSession = (id: string, newTitle: string) => {
    renameSession(id, newTitle);
    showToast('Chat renamed', 'success');
  };

  const handleRetry = () => {
    if (!loading && lastQueryRef.current) {
      onAsk({ preventDefault: () => {} } as unknown as React.FormEvent);
    }
  };

  return (
    <main className="w-full h-screen flex relative overflow-hidden" style={{ backgroundColor: COLORS.background }}>
      {/* Mobile Overlay - removed click to close functionality */}
      {sidebarOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black bg-opacity-30 z-30 pointer-events-none"
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
            onRenameSession={handleRenameSession}
            loading={loading}
          />


      {/* Main column */}
      <section className="flex-1 flex flex-col h-screen overflow-hidden">
            <div className="w-full max-w-5xl mx-auto px-6 pt-6 pb-2 flex-shrink-0">
              <h1 className="text-2xl font-semibold" style={{ color: COLORS.dark }}>PH RoadWise</h1>
            </div>

        {/* Messages list - scrollable */}
        <div 
          ref={messagesContainerRef}
          className="flex-1 w-full max-w-5xl mx-auto px-6 overflow-y-auto space-y-4" 
          aria-live="polite"
        >
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <EmptyState onExampleClick={handleExampleClick} />
            </div>
          ) : (
            <>
              {loading && messages.length === 0 && <MessageSkeleton />}
              {messages.map((m, idx) => (
                <ChatMessage
                  key={idx}
                  message={m}
                  isLast={idx === messages.length - 1}
                  onRegenerate={regenerateLast}
                  loading={loading}
                  onCopy={handleCopyMessage}
                />
              ))}
              {isTyping && <TypingIndicator />}
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

      {/* Toast Container */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Scroll to Bottom Button */}
      <ScrollToBottom onClick={handleScrollToBottom} visible={showScrollButton} />
    </main>
  );
}
