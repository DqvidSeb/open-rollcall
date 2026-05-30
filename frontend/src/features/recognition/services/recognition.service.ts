// Recognition service — stub, to be implemented
import type { RecognitionResult } from '../types';

export const recognitionService = {
  recognize: async (_imageBlob: Blob, _sessionId: string): Promise<RecognitionResult> => {
    // TODO: POST /api/v1/recognition/recognize (multipart with frame)
    throw new Error('Not implemented');
  },

  checkIn: async (_studentId: string, _sessionId: string): Promise<void> => {
    // TODO: POST /api/v1/recognition/checkin
    throw new Error('Not implemented');
  },

  checkOut: async (_studentId: string, _sessionId: string): Promise<void> => {
    // TODO: POST /api/v1/recognition/checkout
    throw new Error('Not implemented');
  },
};
