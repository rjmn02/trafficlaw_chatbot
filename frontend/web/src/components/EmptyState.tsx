import React from 'react';
import { COLORS } from '../constants';

interface EmptyStateProps {
  onExampleClick?: (question: string) => void;
}

const exampleQuestions = [
  "What are the penalties for speeding?",
  "How do I renew my driver's license?",
  "What are the requirements for a student permit?",
  "What is the speed limit on highways?",
];

export function EmptyState({ onExampleClick }: EmptyStateProps) {
  return (
    <div className="w-full h-full flex items-center justify-center px-4">
      <div className="text-center max-w-2xl">
        <div className="text-3xl md:text-4xl font-semibold mb-4 animate-fade-in" style={{ color: COLORS.dark }}>
          Your AI learning companion for Philippine roads
        </div>
        <div className="mb-8 animate-fade-in" style={{ color: COLORS.accent, animationDelay: '0.1s' }}>
          Ask about penalties, violations, licensing, and road rules.
        </div>
        {onExampleClick && (
          <div className="mt-8 space-y-2 animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="text-sm mb-3" style={{ color: COLORS.dark, opacity: 0.7 }}>
              Try asking:
            </div>
            <div className="flex flex-wrap gap-2 justify-center">
              {exampleQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => onExampleClick(question)}
                  className="px-4 py-2 rounded-lg text-sm transition-all hover:scale-105 focus:outline-none focus:ring-2"
                  style={{
                    backgroundColor: COLORS.background,
                    color: COLORS.dark,
                    border: `1px solid ${COLORS.accent}`,
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.primary;
                    (e.currentTarget as HTMLButtonElement).style.color = '#ffffff';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.backgroundColor = COLORS.background;
                    (e.currentTarget as HTMLButtonElement).style.color = COLORS.dark;
                  }}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

