// useReports — stub, to be implemented
'use client';

import type { AttendanceReportRow, ReportFilters } from '../types';

interface UseReportsResult {
  rows: AttendanceReportRow[];
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useReports(_filters: ReportFilters = {}): UseReportsResult {
  // TODO: implement with SWR or TanStack Query
  return {
    rows: [],
    isLoading: false,
    error: null,
    refetch: () => {},
  };
}
