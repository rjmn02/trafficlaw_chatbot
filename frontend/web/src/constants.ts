export const COLORS = {
  background: '#d3d3d5',
  dark: '#3d282a',
  accent: '#994828',
  primary: '#ed971e',
} as const;

export const STORAGE_KEYS = {
  sessions: 'tlc.sessions',
  draft: (sessionId: string) => `tlc.draft.${sessionId}`,
} as const;

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

