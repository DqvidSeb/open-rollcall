// useCamera — stub, to be implemented
// Manages webcam access, stream lifecycle, and frame capture
'use client';

import { useRef } from 'react';

interface UseCameraResult {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  isStreaming: boolean;
  error: string | null;
  startCamera: () => Promise<void>;
  stopCamera: () => void;
  captureFrame: () => Blob | null;
}

export function useCamera(): UseCameraResult {
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // TODO: implement getUserMedia, track cleanup on unmount
  return {
    videoRef,
    isStreaming: false,
    error: null,
    startCamera: async () => {},
    stopCamera: () => {},
    captureFrame: () => null,
  };
}
