import React from 'react';
import { COLORS } from '../constants';

interface ScrollToBottomProps {
  onClick: () => void;
  visible: boolean;
}

export function ScrollToBottom({ onClick, visible }: ScrollToBottomProps) {
  if (!visible) return null;

  return (
    <button
      onClick={onClick}
      className="fixed bottom-28 right-6 z-40 p-3 rounded-full shadow-lg transition-all hover:scale-110 focus:outline-none focus:ring-2 md:bottom-24"
      style={{ 
        backgroundColor: COLORS.primary,
        color: '#ffffff'
      }}
      onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.accent; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary; }}
      aria-label="Scroll to bottom"
      title="Scroll to bottom"
    >
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        width="20" 
        height="20" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      >
        <path d="M12 5v14M19 12l-7 7-7-7" />
      </svg>
    </button>
  );
}

