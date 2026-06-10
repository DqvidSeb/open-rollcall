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

  // Mirror horizontally to match the preview (front camera selfie view).
  ctx.save();
  ctx.translate(CAPTURE_SIZE, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, sx, sy, side, side, 0, 0, CAPTURE_SIZE, CAPTURE_SIZE);
  ctx.restore();
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
