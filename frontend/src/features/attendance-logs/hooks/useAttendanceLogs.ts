'use client';

import { useState, useEffect, useCallback } from 'react';
import { attendanceLogsService } from '../services/attendanceLogs.service';
import type { PaginatedAttendanceLogs } from '../types';

interface UseAttendanceLogsOptions {
  /** 1-based page number */
  page:  number;
  /** Rows per page */
  limit: number;
}

export interface UseAttendanceLogsResult {
  data:      PaginatedAttendanceLogs | null;
  isLoading: boolean;
  error:     string | null;
  refetch:   () => void;
}

/**
 * Fetches a paginated list of attendance records from the backend.
 *
 * Re-fetches automatically when page or limit change.
 */
export function useAttendanceLogs({ page, limit }: UseAttendanceLogsOptions): UseAttendanceLogsResult {
  const [data,      setData]      = useState<PaginatedAttendanceLogs | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await attendanceLogsService.list({ page, page_size: limit });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load attendance records');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [page, limit]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
