import React from 'react';
import { ChatMessage as ChatMessageType } from '../types';
import { IconCopy, IconRefresh } from '../icons';
import { renderMarkdown } from '../utils/markdown';
import { COLORS } from '../constants';

interface ChatMessageProps {
  message: ChatMessageType;
  isLast: boolean;
  onRegenerate?: () => void;
  loading: boolean;
  onCopy?: (content: string) => void;
}

function formatTimestamp(timestamp?: number): string {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function ChatMessage({ message, isLast, onRegenerate, loading, onCopy }: ChatMessageProps) {
  const animationClass = message.role === 'user' ? 'animate-slide-in-right' : 'animate-slide-in-left';
  
  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} ${animationClass}`}>
      <div
        className="relative rounded-xl p-5 leading-relaxed shadow-md border-2 max-w-[90%]"
        style={{
          backgroundColor: message.role === "user" ? COLORS.dark : '#ffffff',
          color: message.role === "user" ? COLORS.background : COLORS.dark,
          borderColor: message.role === "user" ? COLORS.accent : COLORS.primary
        }}
      >
        <div className="flex items-center justify-between mb-2">
          <span 
            className="text-[11px] px-2 py-0.5 rounded-full font-medium"
            style={{
              backgroundColor: message.role === 'user' ? COLORS.accent : COLORS.primary,
              color: message.role === 'user' ? COLORS.background : COLORS.dark
            }}
          >
            {message.role === 'user' ? 'You' : 'Assistant'}
          </span>
          <div className="flex items-center gap-1">
            {message.role === 'assistant' && isLast && onRegenerate && (
              <button
                type="button"
                className="p-1.5 rounded-full cursor-pointer focus:outline-none focus:ring-2 transition-colors"
                style={{ color: COLORS.accent }}
                onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#ed971e20'; }}
                onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
                onClick={onRegenerate}
                title="Regenerate"
                aria-label="Regenerate"
                disabled={loading}
              >
                <IconRefresh />
              </button>
            )}
            <button
              className="p-1.5 rounded-full cursor-pointer focus:outline-none focus:ring-2 transition-colors"
              style={{ color: message.role === 'user' ? COLORS.primary : COLORS.accent }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = message.role === 'user' ? '#99482840' : '#ed971e30'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(message.content);
                  onCopy?.(message.content);
                } catch (err) {
                  // Silently fail if clipboard API is unavailable
                  console.error('Failed to copy to clipboard:', err);
                }
              }}
              title="Copy"
              aria-label="Copy message"
            >
              <IconCopy />
            </button>
          </div>
        </div>
        <div className="whitespace-pre-wrap">{renderMarkdown(message.content)}</div>
        {message.timestamp && (
          <div className="text-xs mt-2 opacity-60" style={{ color: message.role === "user" ? COLORS.background : COLORS.dark }}>
            {formatTimestamp(message.timestamp)}
          </div>
        )}
      </div>
    </div>
  );
}

