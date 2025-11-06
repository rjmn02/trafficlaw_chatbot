import React from 'react';
import { COLORS } from '../constants';

export function MessageSkeleton() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div
        className="rounded-xl p-5 shadow-md border-2 max-w-[90%] w-64"
        style={{
          backgroundColor: '#ffffff',
          borderColor: COLORS.primary
        }}
      >
        <div className="flex items-center gap-2 mb-3">
          <div 
            className="w-16 h-4 rounded"
            style={{ backgroundColor: COLORS.background }}
          />
        </div>
        <div className="space-y-2">
          <div 
            className="h-4 rounded w-full"
            style={{ backgroundColor: COLORS.background }}
          />
          <div 
            className="h-4 rounded w-3/4"
            style={{ backgroundColor: COLORS.background }}
          />
          <div 
            className="h-4 rounded w-5/6"
            style={{ backgroundColor: COLORS.background }}
          />
        </div>
      </div>
    </div>
  );
}

