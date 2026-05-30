// useRecognition — stub, to be implemented
// Orchestrates capture → API → result display loop
'use client';

import type { LiveRecognitionState } from '../types';

interface UseRecognitionOptions {
  sessionId: string;
  autoStart?: boolean;
}

interface UseRecognitionResult extends LiveRecognitionState {
  start: () => void;
  stop: () => void;
  clearResults: () => void;
}

export function useRecognition(_options: UseRecognitionOptions): UseRecognitionResult {
  // TODO: implement polling loop with useCamera + recognitionService
  return {
    isActive: false,
    sessionId: null,
    results: [],
    error: null,
    start: () => {},
    stop: () => {},
    clearResults: () => {},
  };
}
