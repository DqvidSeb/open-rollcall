'use client';

import { useCallback, useEffect, useState } from 'react';
import { faceEnrollmentService } from '../services/faceEnrollment.service';
import type { FaceStatus } from '../types';

interface UseFaceEnrollmentStatusResult {
  status:    FaceStatus | null;
  isLoading: boolean;
  error:     string | null;
  refetch:   () => void;
}

/**
 * Fetches whether the given employee already has a face registered.
 * Pass `null` to skip fetching (e.g. for non-employee persons).
 */
export function useFaceEnrollmentStatus(employeeId: string | null): UseFaceEnrollmentStatusResult {
  const [status, setStatus]       = useState<FaceStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]         = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!employeeId) return;
    setIsLoading(true);
    setError(null);
    try {
      setStatus(await faceEnrollmentService.getStatus(employeeId));
    } catch {
      setError('status-error');
    } finally {
      setIsLoading(false);
    }
  }, [employeeId]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  return { status, isLoading, error, refetch: fetchStatus };
}
