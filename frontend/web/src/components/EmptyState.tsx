import React from 'react';
import { COLORS } from '../constants';

export function EmptyState() {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="text-center">
        <div className="text-3xl md:text-4xl font-semibold mb-6" style={{ color: COLORS.dark }}>
          A small RAG assistant for Philippine traffic laws
        </div>
        <div style={{ color: COLORS.accent }}>
          Ask about penalties, violations, licensing, and road rules.
        </div>
      </div>
    </div>
  );
}

