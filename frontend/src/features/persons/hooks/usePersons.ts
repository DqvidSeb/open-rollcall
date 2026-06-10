'use client';

import { useState, useEffect, useCallback } from 'react';
import { personsService } from '../services/persons.service';
import type { PaginatedPersons } from '../types';

interface UsePersonsOptions {
  /** 1-based page number — converted to offset internally */
  page:  number;
  /** Rows per page */
  limit: number;
}

export interface UsePersonsResult {
  data:      PaginatedPersons | null;
  isLoading: boolean;
  error:     string | null;
  refetch:   () => void;
}

/**
 * Fetches a paginated list of persons (employees + students) from the backend.
 *
 * Converts 1-based `page` + `limit` to the backend's `offset`/`limit` params:
 *   offset = (page - 1) * limit
 *
 * Re-fetches automatically when page or limit change.
 */
export function usePersons({ page, limit }: UsePersonsOptions): UsePersonsResult {
  const [data,      setData]      = useState<PaginatedPersons | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await personsService.list({
        offset: (page - 1) * limit,
        limit,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load people');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [page, limit]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
