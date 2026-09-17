import { useState, useCallback, useEffect } from 'react';
import { listSessions, clearHistory } from '@/lib/api';
import type { SessionSummary } from '@/lib/types';

export function useSessionHistory(currentSessionId: string) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  
  const fetchSessions = useCallback(async () => {
    const res = await listSessions(); // Fetches last 50 latest first
    if (res.success) setSessions(res.data || []);
  }, []);

  const deleteSession = useCallback(async (id: string) => {
    await clearHistory(id); // Existing backend delete route
    fetchSessions(); // Refresh list
  }, [fetchSessions]);

  // Refetch when currentSessionId changes (meaning new chat started or swapped)
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchSessions();
  }, [currentSessionId, fetchSessions]);

  return { sessions, fetchSessions, deleteSession };
}
