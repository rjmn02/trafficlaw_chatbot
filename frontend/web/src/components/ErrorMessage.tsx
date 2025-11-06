import React from 'react';
import { COLORS } from '../constants';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  loading: boolean;
}

export function ErrorMessage({ message, onRetry, loading }: ErrorMessageProps) {
  return (
    <div className="mt-3 border-2 rounded-lg p-3 shadow-md" style={{ borderColor: COLORS.accent, backgroundColor: '#ed971e20', color: COLORS.dark }}>
      {message}
      {onRetry && (
        <button
          className="ml-3 underline text-sm font-medium"
          style={{ color: COLORS.accent }}
          onClick={(e) => {
            e.preventDefault();
            if (!loading) onRetry();
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}

