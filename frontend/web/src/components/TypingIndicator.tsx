import React from 'react';
import { COLORS } from '../constants';

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-2">
      <div className="flex gap-1">
        <div 
          className="typing-dot w-2 h-2 rounded-full"
          style={{ backgroundColor: COLORS.accent }}
        />
        <div 
          className="typing-dot w-2 h-2 rounded-full"
          style={{ backgroundColor: COLORS.accent }}
        />
        <div 
          className="typing-dot w-2 h-2 rounded-full"
          style={{ backgroundColor: COLORS.accent }}
        />
      </div>
      <span className="text-xs ml-2" style={{ color: COLORS.accent }}>Assistant is typing...</span>
    </div>
  );
}

