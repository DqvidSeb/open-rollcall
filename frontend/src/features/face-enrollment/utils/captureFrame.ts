import { CAPTURE_SIZE, JPEG_QUALITY } from '../constants';

/**
 * Draws the current video frame into a square canvas (center-cropped),
 * matching the framing shown by the oval guide overlay.
 */
export function drawVideoFrame(video: HTMLVideoElement, canvas: HTMLCanvasElement): void {
  const { videoWidth, videoHeight } = video;
  if (!videoWidth || !videoHeight) return;

  const side = Math.min(videoWidth, videoHeight);
  const sx = (videoWidth - side) / 2;
  const sy = (videoHeight - side) / 2;

  canvas.width = CAPTURE_SIZE;
  canvas.height = CAPTURE_SIZE;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // NOT mirrored: the preview mirrors via CSS (scaleX(-1)), but frames sent
  // to the backend must match reality — ArcFace embeddings are not
  // mirror-invariant, and the camera client also sends unmirrored faces.
  ctx.drawImage(video, sx, sy, side, side, 0, 0, CAPTURE_SIZE, CAPTURE_SIZE);
}

/** Returns the canvas contents as a base64 JPEG string (no data URL prefix). */
export function canvasToBase64(canvas: HTMLCanvasElement): string {
  const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
  return dataUrl.split(',')[1] ?? '';
}

/** Returns a small data URL thumbnail for the "captured" confirmation overlay. */
export function canvasToThumbnail(canvas: HTMLCanvasElement): string {
  return canvas.toDataURL('image/jpeg', 0.7);
}
