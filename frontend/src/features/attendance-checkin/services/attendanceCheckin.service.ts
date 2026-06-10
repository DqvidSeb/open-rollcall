import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type { AttendanceCheckResult } from '../types';

/**
 * Attendance check-in/check-out API service.
 * Maps to the backend's POST /api/v1/face/check-in pipeline: recognizes the
 * face in the frame and records a check-in or check-out automatically.
 */
export const attendanceCheckinService = {
  /**
   * POST /api/v1/face/check-in
   * Sends a single base64 JPEG frame (no data URL prefix).
   *
   * Possible responses (surfaced via `ApiError.status`):
   *  - 201: recognized — attendance recorded.
   *  - 422: face not recognized, or outside the configured check-in/out window.
   *  - 409: employee already completed both check-in and check-out today.
   */
  checkIn: (imageBase64: string): Promise<AttendanceCheckResult> =>
    apiClient.post<AttendanceCheckResult>(ENDPOINTS.FACE_CHECK_IN, {
      image_base64: imageBase64,
    }),
};
