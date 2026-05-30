'use client';

import { useState, useEffect, useCallback } from 'react';
import { departmentsService } from '../services/departments.service';
import type { PaginatedDepartments } from '../types';

interface UseDepartmentsOptions {
  /** 1-based page number — converted to offset internally */
  page:  number;
  /** Rows per page */
  limit: number;
}

export interface UseDepartmentsResult {
  data:      PaginatedDepartments | null;
  isLoading: boolean;
  error:     string | null;
  refetch:   () => void;
}

/**
 * Fetches a paginated list of departments from the backend.
 *
 * Converts 1-based `page` + `limit` to the backend's `offset`/`limit` params:
 *   offset = (page - 1) * limit
 *
 * Re-fetches automatically when page or limit change.
 */
export function useDepartments({ page, limit }: UseDepartmentsOptions): UseDepartmentsResult {
  const [data,      setData]      = useState<PaginatedDepartments | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await departmentsService.list({
        offset: (page - 1) * limit,
        limit,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load departments');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [page, limit]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
