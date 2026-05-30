export type RecognitionStatus = 'idle' | 'scanning' | 'recognized' | 'unknown' | 'error';

export interface RecognitionResult {
  studentId?: string;
  studentName?: string;
  confidence: number;
  status: RecognitionStatus;
  timestamp: string;
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
}

export interface LiveRecognitionState {
  isActive: boolean;
  sessionId: string | null;
  results: RecognitionResult[];
  error: string | null;
}
