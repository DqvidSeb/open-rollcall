// RecognitionOverlay — stub, to be implemented
// Draws bounding boxes and confidence labels on canvas
'use client';

import type { RecognitionResult } from '../types';

interface RecognitionOverlayProps {
  results: RecognitionResult[];
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
}

export function RecognitionOverlay(_props: RecognitionOverlayProps) {
  // TODO: use canvas 2D context to draw boxes
  return null;
}
