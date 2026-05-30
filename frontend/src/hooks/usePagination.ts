'use client';

import { useState } from 'react';

interface UsePaginationOptions {
  initialPage?: number;
  initialLimit?: number;
}

interface UsePaginationResult {
  page: number;
  limit: number;
  setPage: (page: number) => void;
  setLimit: (limit: number) => void;
  reset: () => void;
}

export function usePagination({
  initialPage = 1,
  initialLimit = 20,
}: UsePaginationOptions = {}): UsePaginationResult {
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);

  return {
    page,
    limit,
    setPage,
    setLimit,
    reset: () => setPage(initialPage),
  };
}
