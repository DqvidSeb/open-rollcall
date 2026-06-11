'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { faceEnrollmentService } from '../services/faceEnrollment.service';
import { canvasToBase64, canvasToThumbnail, drawVideoFrame } from '../utils/captureFrame';
import { evaluateFrameQuality, type QualityResult } from '../utils/imageQuality';
import {
  BETWEEN_CAPTURE_SECONDS, CONFIRMATION_DISPLAY_MS,
  POSITIONING_SECONDS, TOTAL_SAMPLES,
} from '../constants';
import type { CapturedSample, CapturePhase, FaceEnrollResult } from '../types';

interface UseFaceCaptureOptions {
  personId: string;
  videoRef:   React.RefObject<HTMLVideoElement | null>;
  /** True once the camera stream is attached and playing. */
  cameraReady: boolean;
  onEnrolled: (result: FaceEnrollResult) => void;
}

interface UseFaceCaptureResult {
  phase:          CapturePhase;
  currentStep:    number;
  countdown:      number;
  thumbnail:      string | null;
  qualityWarning: QualityResult['reasonKey'];
  error:          string | null;
  retry:          () => void;
}

/**
 * Drives the guided 5-photo capture flow:
 * positioning countdown → quality-checked capture → confirmation →
 * repeat for each angle → upload to the backend.
 */
export function useFaceCapture({
  personId, videoRef, cameraReady, onEnrolled,
}: UseFaceCaptureOptions): UseFaceCaptureResult {
  const [phase, setPhase]             = useState<CapturePhase>('requesting-camera');
  const [currentStep, setCurrentStep] = useState(0);
  const [countdown, setCountdown]     = useState(POSITIONING_SECONDS);
  const [thumbnail, setThumbnail]     = useState<string | null>(null);
  const [qualityWarning, setQualityWarning] = useState<QualityResult['reasonKey']>(null);
  const [error, setError]             = useState<string | null>(null);

  const samplesRef = useRef<CapturedSample[]>([]);
  const [canvas]   = useState<HTMLCanvasElement | null>(() =>
    typeof document === 'undefined' ? null : document.createElement('canvas'));

  // Camera becomes ready → start the positioning countdown.
  useEffect(() => {
    if (cameraReady && phase === 'requesting-camera') {
      setPhase('positioning');
      setCountdown(POSITIONING_SECONDS);
    }
  }, [cameraReady, phase]);

  const captureCurrentFrame = useCallback(() => {
    const video = videoRef.current;
    if (!video || !canvas) return;

    drawVideoFrame(video, canvas);
    const quality = evaluateFrameQuality(canvas);

    if (!quality.ok) {
      setQualityWarning(quality.reasonKey);
      setCountdown(BETWEEN_CAPTURE_SECONDS);
      return;
    }

    setQualityWarning(null);
    samplesRef.current.push({ index: currentStep, base64: canvasToBase64(canvas) });
    setThumbnail(canvasToThumbnail(canvas));
    setPhase('captured');
  }, [currentStep, videoRef, canvas]);

  // Countdown ticker.
  useEffect(() => {
    if (phase !== 'positioning' && phase !== 'countdown') return;

    if (countdown <= 0) {
      captureCurrentFrame();
      return;
    }

    const timer = setTimeout(() => setCountdown(c => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [phase, countdown, captureCurrentFrame]);

  // After a successful capture, advance to the next step or upload.
  useEffect(() => {
    if (phase !== 'captured') return;

    const timer = setTimeout(() => {
      const nextStep = currentStep + 1;
      if (nextStep < TOTAL_SAMPLES) {
        setCurrentStep(nextStep);
        setCountdown(BETWEEN_CAPTURE_SECONDS);
        setPhase('countdown');
      } else {
        setPhase('uploading');
      }
    }, CONFIRMATION_DISPLAY_MS);

    return () => clearTimeout(timer);
  }, [phase, currentStep]);

  // Upload once all samples are captured.
  useEffect(() => {
    if (phase !== 'uploading') return;

    let cancelled = false;
    const upload = async () => {
      try {
        const images = samplesRef.current
          .sort((a, b) => a.index - b.index)
          .map(s => s.base64);
        const result = await faceEnrollmentService.enroll(personId, images);
        if (cancelled) return;
        setPhase('success');
        onEnrolled(result);
      } catch {
        if (!cancelled) {
          setError('upload-error');
          setPhase('error');
        }
      }
    };

    upload();
    return () => { cancelled = true; };
  }, [phase, personId, onEnrolled]);

  const retry = useCallback(() => {
    samplesRef.current = [];
    setCurrentStep(0);
    setThumbnail(null);
    setQualityWarning(null);
    setError(null);
    setCountdown(POSITIONING_SECONDS);
    setPhase(cameraReady ? 'positioning' : 'requesting-camera');
  }, [cameraReady]);

  return { phase, currentStep, countdown, thumbnail, qualityWarning, error, retry };
}
