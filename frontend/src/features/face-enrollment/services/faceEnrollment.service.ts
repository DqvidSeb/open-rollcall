import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type { FaceEnrollResult, FaceStatus } from '../types';

/**
 * Face enrollment API service.
 * Maps directly to the backend /api/v1/face endpoints (employees and students).
 */
export const faceEnrollmentService = {
  /** GET /api/v1/face/status/:personId */
  getStatus: (personId: string): Promise<FaceStatus> =>
    apiClient.get<FaceStatus>(ENDPOINTS.FACE_STATUS(personId)),

  /**
   * POST /api/v1/face/enroll/:personId
   * Sends the captured frames (base64 JPEG, no data URL prefix).
   * Replaces any previously stored face encodings for this person.
   */
  enroll: (personId: string, imagesBase64: string[]): Promise<FaceEnrollResult> =>
    apiClient.post<FaceEnrollResult>(ENDPOINTS.FACE_ENROLL(personId), {
      images_base64: imagesBase64,
    }, {
      // Model download on first run can take a while server-side.
      signal: AbortSignal.timeout(180_000),
    }),

  /** DELETE /api/v1/face/encodings/:personId */
  deleteEncodings: (personId: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.FACE_ENCODINGS(personId)),
};
