"use client";
import React from 'react';
import { StoredSession } from '../types';
import { COLORS } from '../constants';
import { IconMenu, IconPlus, IconSearch, IconMessage, IconEdit, IconTrash, IconChevronRight, IconChevronLeft, IconMessageSquare } from '../icons';

interface SidebarProps {
  sessions: StoredSession[];
  filteredSessions: StoredSession[];
  currentSessionId: string;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  onToggleSidebar?: () => void;
  onNewChat: () => void;
  onSwitchSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onRenameSession: (id: string, newTitle: string) => void;
  loading: boolean;
}

export function Sidebar({
  sessions,
  filteredSessions,
  currentSessionId,
  searchQuery,
  setSearchQuery,
  sidebarOpen,
  sidebarCollapsed,
  setSidebarCollapsed,
  onToggleSidebar,
  onNewChat,
  onSwitchSession,
  onDeleteSession,
  onRenameSession,
  loading,
}: SidebarProps) {
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editValue, setEditValue] = React.useState<string>("");
  const editInputRef = React.useRef<HTMLInputElement | null>(null);

  const handleStartEdit = (session: StoredSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditValue(session.title);
    setTimeout(() => editInputRef.current?.focus(), 0);
  };

  const handleSaveEdit = (id: string, e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (editValue.trim()) {
      onRenameSession(id, editValue.trim());
    }
    setEditingId(null);
    setEditValue("");
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditValue("");
  };
  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={onToggleSidebar}
        className="fixed right-4 top-4 z-50 md:hidden p-2 rounded-lg shadow-lg transition-all"
        style={{ backgroundColor: COLORS.primary, color: '#ffffff' }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.accent; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary; }}
        aria-label="Toggle sidebar"
      >
        <IconMenu className="w-6 h-6" />
      </button>

      {/* Sidebar - ChatGPT Style */}
      <aside 
        className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:static left-0 top-0 h-screen z-40 flex flex-col transition-all duration-300 ease-in-out shadow-2xl overflow-hidden`}
        style={{ 
          width: sidebarCollapsed ? '60px' : '260px',
          backgroundColor: COLORS.background,
          borderRight: `1px solid ${COLORS.accent}`
        }}
      >
        {!sidebarCollapsed ? (
          <>
            <div className="p-4 border-b" style={{ borderColor: COLORS.accent }}>
              <button 
                onClick={onNewChat} 
                className="w-full text-white text-sm px-4 py-2.5 rounded-lg transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none font-medium mb-3 flex items-center gap-2"
                style={{ backgroundColor: COLORS.primary }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.accent; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary; }}
                disabled={loading}
              >
                <IconPlus className="w-4 h-4" />
                <span>New chat</span>
              </button>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search chats"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 pr-8 rounded-lg border text-sm focus:outline-none focus:ring-2"
                  style={{ 
                    borderColor: COLORS.accent,
                    backgroundColor: '#ffffff',
                    color: COLORS.dark
                  }}
                />
                <IconSearch className="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2" style={{ color: COLORS.accent }} />
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-2 min-h-0">
              <div className="text-xs font-semibold mb-2 px-2" style={{ color: COLORS.accent }}>Recent</div>
              <div className="space-y-1">
                {filteredSessions.map(s => (
                  <div 
                    key={s.id} 
                    className={`group flex items-center gap-2 p-2.5 rounded-lg cursor-pointer transition-all ${
                      currentSessionId === s.id 
                        ? '' 
                        : 'hover:bg-opacity-50'
                    }`}
                    style={{
                      backgroundColor: currentSessionId === s.id ? COLORS.primary : 'transparent',
                      color: COLORS.dark
                    }}
                    onClick={() => {
                      if (editingId !== s.id) {
                        onSwitchSession(s.id);
                      }
                    }}
                  >
                    <IconMessage className="w-4 h-4 flex-shrink-0" style={{ color: currentSessionId === s.id ? COLORS.dark : COLORS.accent }} />
                    {editingId === s.id ? (
                      <form 
                        onSubmit={(e) => handleSaveEdit(s.id, e)}
                        className="flex-1 flex items-center gap-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <input
                          ref={editInputRef}
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          onBlur={() => handleSaveEdit(s.id)}
                          onKeyDown={(e) => {
                            if (e.key === 'Escape') {
                              handleCancelEdit();
                            } else if (e.key === 'Enter') {
                              e.preventDefault();
                              handleSaveEdit(s.id);
                            }
                          }}
                          className="flex-1 text-sm px-2 py-1 rounded border focus:outline-none focus:ring-1"
                          style={{ 
                            borderColor: COLORS.accent,
                            backgroundColor: '#ffffff',
                            color: COLORS.dark
                          }}
                          onClick={(e) => e.stopPropagation()}
                          autoFocus
                        />
                      </form>
                    ) : (
                      <>
                        <span 
                          className="flex-1 text-sm truncate"
                          onDoubleClick={(e) => handleStartEdit(s, e)}
                          title="Double-click to rename"
                        >
                          {s.title || 'Untitled'}
                        </span>
                        <button 
                          className="opacity-0 group-hover:opacity-100 transition-all p-1.5 rounded-lg active:scale-90" 
                          style={{ 
                            color: COLORS.accent,
                            backgroundColor: 'transparent'
                          }}
                          onMouseEnter={(e) => {
                            const target = e.currentTarget;
                            if (target) {
                              target.style.backgroundColor = '#99482820';
                              target.style.color = COLORS.accent;
                              target.style.transform = 'scale(1.1)';
                            }
                          }}
                          onMouseLeave={(e) => {
                            const target = e.currentTarget;
                            if (target) {
                              target.style.backgroundColor = 'transparent';
                              target.style.transform = 'scale(1)';
                            }
                          }}
                          onClick={(e) => handleStartEdit(s, e)}
                          title="Rename chat"
                        >
                          <IconEdit />
                        </button>
                        <button 
                          className="opacity-0 group-hover:opacity-100 transition-all p-1.5 rounded-lg active:scale-90" 
                          style={{ 
                            color: COLORS.accent,
                            backgroundColor: 'transparent'
                          }}
                          onMouseEnter={(e) => {
                            const target = e.currentTarget;
                            if (target) {
                              target.style.backgroundColor = '#99482820';
                              target.style.color = COLORS.accent;
                              target.style.transform = 'scale(1.1)';
                            }
                          }}
                          onMouseLeave={(e) => {
                            const target = e.currentTarget;
                            if (target) {
                              target.style.backgroundColor = 'transparent';
                              target.style.transform = 'scale(1)';
                            }
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            const target = e.currentTarget;
                            if (!target) return;
                            target.style.transform = 'scale(0.9)';
                            target.style.backgroundColor = '#99482840';
                            setTimeout(() => {
                              if (target) {
                                target.style.transform = 'scale(1)';
                              }
                              onDeleteSession(s.id);
                            }, 150);
                          }}
                          title="Delete chat"
                        >
                          <IconTrash />
                        </button>
                      </>
                    )}
                  </div>
                ))}
                {filteredSessions.length === 0 && (
                  <div className="text-sm text-center py-8 px-2" style={{ color: COLORS.accent }}>
                    {searchQuery ? 'No chats found' : 'No saved chats yet.<br/>Start a conversation!'}
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center py-3 gap-2">
            <button 
              onClick={onNewChat} 
              className="relative group p-2.5 rounded-lg transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
              style={{ backgroundColor: COLORS.primary, color: '#ffffff' }}
              onMouseEnter={(e) => { 
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.accent;
                const tooltip = e.currentTarget.querySelector('.tooltip');
                if (tooltip) (tooltip as HTMLElement).style.opacity = '1';
              }}
              onMouseLeave={(e) => { 
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary;
                const tooltip = e.currentTarget.querySelector('.tooltip');
                if (tooltip) (tooltip as HTMLElement).style.opacity = '0';
              }}
              disabled={loading}
            >
              <IconPlus className="w-5 h-5" />
              <div className="tooltip absolute left-full ml-2 px-2 py-1 rounded text-xs whitespace-nowrap pointer-events-none opacity-0 transition-opacity z-50" style={{ backgroundColor: COLORS.dark, color: COLORS.background }}>
                New chat
              </div>
            </button>
            <div className="flex-1 overflow-y-auto w-full px-2 space-y-1 min-h-0">
              {sessions.slice(0, 10).map(s => (
                <button
                  key={s.id}
                  onClick={() => onSwitchSession(s.id)}
                  className={`relative group w-full p-2.5 rounded-lg transition-all ${
                    currentSessionId === s.id ? '' : 'hover:bg-opacity-50'
                  }`}
                  style={{
                    backgroundColor: currentSessionId === s.id ? COLORS.primary : 'transparent',
                    color: COLORS.dark
                  }}
                >
                  <IconMessageSquare className="w-5 h-5 mx-auto" style={{ color: currentSessionId === s.id ? COLORS.dark : COLORS.accent }} />
                  <div className="tooltip absolute left-full ml-2 px-2 py-1 rounded text-xs whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-50" style={{ backgroundColor: COLORS.dark, color: COLORS.background }}>
                    {s.title || 'Untitled'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
        {/* Collapse Button - Hidden on mobile */}
        <div className="hidden md:block p-2 border-t" style={{ borderColor: COLORS.accent }}>
          <button
            onClick={(e) => {
              const target = e.currentTarget;
              if (!target) return;
              target.style.transform = 'scale(0.95)';
              setTimeout(() => {
                if (target) {
                  target.style.transform = 'scale(1)';
                }
                setSidebarCollapsed(!sidebarCollapsed);
              }, 100);
            }}
            className="w-full p-2 rounded-lg transition-all flex items-center justify-center group relative active:scale-95"
            style={{ 
              color: COLORS.dark,
              backgroundColor: 'transparent'
            }}
            onMouseEnter={(e) => {
              const target = e.currentTarget;
              if (target) {
                target.style.backgroundColor = '#ed971e30';
                target.style.transform = 'scale(1.05)';
              }
            }}
            onMouseLeave={(e) => {
              const target = e.currentTarget;
              if (target) {
                target.style.backgroundColor = 'transparent';
                target.style.transform = 'scale(1)';
              }
            }}
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? (
              <IconChevronRight className="w-5 h-5" />
            ) : (
              <IconChevronLeft className="w-5 h-5" />
            )}
            {!sidebarCollapsed && (
              <div className="tooltip absolute left-full ml-2 px-2 py-1 rounded text-xs whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-50" style={{ backgroundColor: COLORS.dark, color: COLORS.background }}>
                Collapse
              </div>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}

