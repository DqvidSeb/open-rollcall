'use client';

import { useState, useEffect, useCallback } from 'react';
import { positionsService } from '../services/positions.service';
import type { PaginatedPositions } from '../types';

interface UsePositionsOptions {
  /** 1-based page number — converted to offset internally */
  page:  number;
  /** Rows per page */
  limit: number;
}

export interface UsePositionsResult {
  data:      PaginatedPositions | null;
  isLoading: boolean;
  error:     string | null;
  refetch:   () => void;
}

/**
 * Fetches a paginated list of positions from the backend.
 *
 * Converts 1-based `page` + `limit` to the backend's `offset`/`limit` params:
 *   offset = (page - 1) * limit
 *
 * Re-fetches automatically when page or limit change.
 */
export function usePositions({ page, limit }: UsePositionsOptions): UsePositionsResult {
  const [data,      setData]      = useState<PaginatedPositions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await positionsService.list({
        offset: (page - 1) * limit,
        limit,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load positions');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [page, limit]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
