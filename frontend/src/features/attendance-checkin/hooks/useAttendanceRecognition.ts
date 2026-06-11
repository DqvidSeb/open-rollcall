'use client';

import { useEffect, useRef, useState } from 'react';
import { ApiError } from '@/lib/api/client';
import { attendanceCheckinService } from '../services/attendanceCheckin.service';
import { canvasToBase64, drawWideVideoFrame } from '../utils/captureFrame';
import {
  CONFLICT_DISPLAY_MS, NO_MATCH_DISPLAY_MS,
  RECOGNITION_INTERVAL_MS, SUCCESS_DISPLAY_MS,
} from '../constants';
import type { AttendanceCheckResult, RecognitionPhase } from '../types';

interface UseAttendanceRecognitionOptions {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  /** True once the camera stream is attached and playing. */
  cameraReady: boolean;
}

interface UseAttendanceRecognitionResult {
  phase:    RecognitionPhase;
  result:   AttendanceCheckResult | null;
  message:  string | null;
  retry:    () => void;
}

/**
 * Drives a continuous "scan -> recognize" loop while the camera is active,
 * mirroring the backend's `camera_client.py attend` script: frames are sent
 * at a steady pace, a successful recognition is held on screen, transient
 * "no match" hints fade quickly, and out-of-window/conflict responses are
 * surfaced to the user.
 */
export function useAttendanceRecognition({
  videoRef, cameraReady,
}: UseAttendanceRecognitionOptions): UseAttendanceRecognitionResult {
  const [phase, setPhase]     = useState<RecognitionPhase>('requesting-camera');
  const [result, setResult]   = useState<AttendanceCheckResult | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const busyRef = useRef(false);
  const [canvas] = useState<HTMLCanvasElement | null>(() =>
    typeof document === 'undefined' ? null : document.createElement('canvas'));

  // Camera becomes ready -> start scanning.
  useEffect(() => {
    if (cameraReady && phase === 'requesting-camera') {
      setPhase('scanning');
    }
  }, [cameraReady, phase]);

  // Recognition loop: only runs while actively scanning.
  useEffect(() => {
    if (phase !== 'scanning' || !cameraReady) return;

    const tick = async () => {
      if (busyRef.current) return;
      const video = videoRef.current;
      if (!video || !canvas) return;
      if (!drawWideVideoFrame(video, canvas)) return;

      busyRef.current = true;
      try {
        const data = await attendanceCheckinService.checkIn(canvasToBase64(canvas));
        setResult(data);
        setPhase('recognized');
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 422 && /horario|window/i.test(err.message)) {
            setMessage(err.message);
            setPhase('blocked');
          } else if (err.status === 409) {
            setMessage(err.message);
            setPhase('no-match');
          } else if (err.status === 422 && /no face detected/i.test(err.message)) {
            // Frame without a face: keep scanning silently, no UI pause.
          } else if (err.status === 422) {
            setPhase('no-match');
          } else {
            setMessage(err.message);
            setPhase('error');
          }
        } else {
          setMessage(null);
          setPhase('error');
        }
      } finally {
        busyRef.current = false;
      }
    };

    const timer = setInterval(tick, RECOGNITION_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [phase, cameraReady, videoRef, canvas]);

  // Auto-resume scanning after a successful recognition or transient hint.
  useEffect(() => {
    if (phase === 'recognized') {
      const timer = setTimeout(() => { setResult(null); setPhase('scanning'); }, SUCCESS_DISPLAY_MS);
      return () => clearTimeout(timer);
    }
    if (phase === 'no-match') {
      const duration = message ? CONFLICT_DISPLAY_MS : NO_MATCH_DISPLAY_MS;
      const timer = setTimeout(() => { setMessage(null); setPhase('scanning'); }, duration);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [phase, message]);

  const retry = () => {
    setResult(null);
    setMessage(null);
    setPhase(cameraReady ? 'scanning' : 'requesting-camera');
  };

  return { phase, result, message, retry };
}
