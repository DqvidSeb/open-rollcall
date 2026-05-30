// useSessions — stub, to be implemented
'use client';

import type { Session, SessionFilters } from '../types';
import type { PaginatedResponse } from '@/types/api';

interface UseSessionsResult {
  data: PaginatedResponse<Session> | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useSessions(_filters: SessionFilters = {}): UseSessionsResult {
  // TODO: implement with SWR or TanStack Query
  return {
    data: null,
    isLoading: false,
    error: null,
    refetch: () => {},
  };
}
