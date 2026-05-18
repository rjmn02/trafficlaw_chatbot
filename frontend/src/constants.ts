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

/** Python backend URL for production builds. No trailing slash. */
const PYTHON_API_URL = (
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '');

/**
 * Build a fetch URL for a FastAPI route.
 *
 * - Dev (default): `/api` + path → Vite proxy rewrites to Python
 * - Dev + VITE_API_URL set: calls Python directly
 * - Prod: `VITE_API_URL` + path
 */
function apiUrl(pythonPath: string): string {
  const useViteProxy = import.meta.env.DEV && !import.meta.env.VITE_API_URL;

  if (useViteProxy) {
    return `/api${pythonPath}`;
  }

  return `${PYTHON_API_URL}${pythonPath}`;
}

export const CHAT_ENDPOINT = apiUrl('/chat');

export function sessionDeleteUrl(sessionId: string): string {
  return apiUrl(`/sessions/${sessionId}`);
}
