"use client";
import React from 'react';
import { StoredSession } from '../types';
import { COLORS } from '../constants';

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
  loading,
}: SidebarProps) {
  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={onToggleSidebar}
        className="fixed left-4 top-4 z-50 md:hidden p-2 rounded-lg shadow-lg transition-all"
        style={{ backgroundColor: COLORS.primary, color: '#ffffff' }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.accent; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary; }}
        aria-label="Toggle sidebar"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
          <path fillRule="evenodd" d="M3 6.75A.75.75 0 013.75 6h16.5a.75.75 0 010 1.5H3.75A.75.75 0 013 6.75zM3 12a.75.75 0 01.75-.75h16.5a.75.75 0 010 1.5H3.75A.75.75 0 013 12zm0 5.25a.75.75 0 01.75-.75h16.5a.75.75 0 010 1.5H3.75a.75.75 0 01-.75-.75z" clipRule="evenodd" />
        </svg>
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
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                  <path d="M8 9a1 1 0 011-1h6a1 1 0 110 2H9a1 1 0 01-1-1zM8 13a1 1 0 011-1h4a1 1 0 110 2H9a1 1 0 01-1-1z" />
                  <path fillRule="evenodd" d="M3 5a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm2 0v14h14V5H5z" clipRule="evenodd" />
                </svg>
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
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2" style={{ color: COLORS.accent }}>
                  <path fillRule="evenodd" d="M10.5 3.75a6.75 6.75 0 100 13.5 6.75 6.75 0 000-13.5zM2.25 10.5a8.25 8.25 0 1114.59 5.28l4.69 4.69a.75.75 0 11-1.06 1.06l-4.69-4.69A8.25 8.25 0 012.25 10.5z" clipRule="evenodd" />
                </svg>
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
                    onClick={() => onSwitchSession(s.id)}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 flex-shrink-0" style={{ color: currentSessionId === s.id ? COLORS.dark : COLORS.accent }}>
                      <path fillRule="evenodd" d="M4.848 2.771A49.144 49.144 0 0112 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 01-3.476.383.39.39 0 00-.297.17l-2.755 4.133a.75.75 0 01-1.248 0l-2.755-4.133a.39.39 0 00-.297-.17 48.9 48.9 0 01-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97zM6.75 8.25a.75.75 0 01.75-.75h9a.75.75 0 010 1.5h-9a.75.75 0 01-.75-.75zm.75 2.25a.75.75 0 000 1.5H12a.75.75 0 000-1.5H7.5z" clipRule="evenodd" />
                    </svg>
                    <span className="flex-1 text-sm truncate">{s.title || 'Untitled'}</span>
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
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                        <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
                      </svg>
                    </button>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M8 9a1 1 0 011-1h6a1 1 0 110 2H9a1 1 0 01-1-1zM8 13a1 1 0 011-1h4a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path fillRule="evenodd" d="M3 5a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm2 0v14h14V5H5z" clipRule="evenodd" />
              </svg>
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
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 mx-auto" style={{ color: currentSessionId === s.id ? COLORS.dark : COLORS.accent }}>
                    <path fillRule="evenodd" d="M4.848 2.771A49.144 49.144 0 0112 2.25c2.43 0 4.817.178 7.152.52 1.978.292 3.348 2.024 3.348 3.97v6.02c0 1.946-1.37 3.678-3.348 3.97a48.901 48.901 0 01-3.476.383.39.39 0 00-.297.17l-2.755 4.133a.75.75 0 01-1.248 0l-2.755-4.133a.39.39 0 00-.297-.17 48.9 48.9 0 01-3.476-.384c-1.978-.29-3.348-2.024-3.348-3.97V6.741c0-1.946 1.37-3.68 3.348-3.97zM6.75 8.25a.75.75 0 01.75-.75h9a.75.75 0 010 1.5h-9a.75.75 0 01-.75-.75zm.75 2.25a.75.75 0 000 1.5H12a.75.75 0 000-1.5H7.5z" clipRule="evenodd" />
                  </svg>
                  <div className="tooltip absolute left-full ml-2 px-2 py-1 rounded text-xs whitespace-nowrap pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-50" style={{ backgroundColor: COLORS.dark, color: COLORS.background }}>
                    {s.title || 'Untitled'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
        {/* Collapse Button */}
        <div className="p-2 border-t" style={{ borderColor: COLORS.accent }}>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path fillRule="evenodd" d="M16.28 11.47a.75.75 0 010 1.06l-7.5 7.5a.75.75 0 01-1.06-1.06L14.69 12 7.72 5.03a.75.75 0 011.06-1.06l7.5 7.5z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path fillRule="evenodd" d="M7.72 12.53a.75.75 0 010-1.06l7.5-7.5a.75.75 0 111.06 1.06L9.31 12l6.97 6.97a.75.75 0 11-1.06 1.06l-7.5-7.5z" clipRule="evenodd" />
              </svg>
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

