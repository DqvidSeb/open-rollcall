'use client';

import { useEffect, useRef, useState } from 'react';

interface UseCameraResult {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  isReady:  boolean;
  error:    string | null;
}

/**
 * Requests access to the user's front-facing camera and attaches the
 * resulting stream to a `<video>` element. Cleans up the stream on unmount.
 */
export function useCamera(active: boolean): UseCameraResult {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    if (!active) {
      setIsReady(false);
      return;
    }

    let stream: MediaStream | null = null;
    let cancelled = false;
    const video = videoRef.current;

    const start = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 960 }, height: { ideal: 720 } },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        if (video) {
          video.srcObject = stream;
          await video.play();
        }
        setIsReady(true);
      } catch {
        if (!cancelled) setError('camera-permission');
      }
    };

    start();

    return () => {
      cancelled = true;
      stream?.getTracks().forEach(track => track.stop());
      if (video) video.srcObject = null;
    };
  }, [active]);

  return { videoRef, isReady, error };
}
