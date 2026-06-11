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
 * Fetches whether the given person (employee or student) already has a
 * face registered. Pass `null` to skip fetching.
 */
export function useFaceEnrollmentStatus(personId: string | null): UseFaceEnrollmentStatusResult {
  const [status, setStatus]       = useState<FaceStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]         = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!personId) return;
    setIsLoading(true);
    setError(null);
    try {
      setStatus(await faceEnrollmentService.getStatus(personId));
    } catch {
      setError('status-error');
    } finally {
      setIsLoading(false);
    }
  }, [personId]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  return { status, isLoading, error, refetch: fetchStatus };
}
