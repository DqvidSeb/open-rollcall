import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type { FaceEnrollResult, FaceStatus } from '../types';

/**
 * Face enrollment API service.
 * Maps directly to the backend /api/v1/face endpoints (employees only).
 */
export const faceEnrollmentService = {
  /** GET /api/v1/face/status/:employeeId */
  getStatus: (employeeId: string): Promise<FaceStatus> =>
    apiClient.get<FaceStatus>(ENDPOINTS.FACE_STATUS(employeeId)),

  /**
   * POST /api/v1/face/enroll/:employeeId
   * Sends the captured frames (base64 JPEG, no data URL prefix).
   * Replaces any previously stored face encodings for this employee.
   */
  enroll: (employeeId: string, imagesBase64: string[]): Promise<FaceEnrollResult> =>
    apiClient.post<FaceEnrollResult>(ENDPOINTS.FACE_ENROLL(employeeId), {
      images_base64: imagesBase64,
    }, {
      // Model download on first run can take a while server-side.
      signal: AbortSignal.timeout(180_000),
    }),

  /** DELETE /api/v1/face/encodings/:employeeId */
  deleteEncodings: (employeeId: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.FACE_ENCODINGS(employeeId)),
};
