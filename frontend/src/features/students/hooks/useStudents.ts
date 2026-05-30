// useStudents — stub, to be implemented
'use client';

import type { Student, StudentFilters } from '../types';
import type { PaginatedResponse } from '@/types/api';

interface UseStudentsResult {
  data: PaginatedResponse<Student> | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useStudents(_filters: StudentFilters = {}): UseStudentsResult {
  // TODO: implement with SWR or TanStack Query
  return {
    data: null,
    isLoading: false,
    error: null,
    refetch: () => {},
  };
}
