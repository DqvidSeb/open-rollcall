// useAttendance — stub, to be implemented
'use client';

import type { AttendanceRecord, AttendanceFilters } from '../types';
import type { PaginatedResponse } from '@/types/api';

interface UseAttendanceResult {
  data: PaginatedResponse<AttendanceRecord> | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useAttendance(_filters: AttendanceFilters = {}): UseAttendanceResult {
  // TODO: implement with SWR or TanStack Query
  return {
    data: null,
    isLoading: false,
    error: null,
    refetch: () => {},
  };
}
