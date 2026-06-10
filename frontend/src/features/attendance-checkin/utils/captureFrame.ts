import { CAPTURE_HEIGHT, CAPTURE_WIDTH, JPEG_QUALITY } from '../constants';

/**
 * Draws the current video frame into a wide (16:9) canvas, center-cropped
 * from the camera stream. Mirrored horizontally to match the selfie preview.
 */
export function drawWideVideoFrame(video: HTMLVideoElement, canvas: HTMLCanvasElement): boolean {
  const { videoWidth, videoHeight } = video;
  if (!videoWidth || !videoHeight) return false;

  const targetRatio = CAPTURE_WIDTH / CAPTURE_HEIGHT;
  const sourceRatio = videoWidth / videoHeight;

  let sx = 0;
  let sy = 0;
  let sw = videoWidth;
  let sh = videoHeight;

  if (sourceRatio > targetRatio) {
    sw = videoHeight * targetRatio;
    sx = (videoWidth - sw) / 2;
  } else {
    sh = videoWidth / targetRatio;
    sy = (videoHeight - sh) / 2;
  }

  canvas.width = CAPTURE_WIDTH;
  canvas.height = CAPTURE_HEIGHT;

  const ctx = canvas.getContext('2d');
  if (!ctx) return false;

  ctx.save();
  ctx.translate(CAPTURE_WIDTH, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, sx, sy, sw, sh, 0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT);
  ctx.restore();
  return true;
}

/** Returns the canvas contents as a base64 JPEG string (no data URL prefix). */
export function canvasToBase64(canvas: HTMLCanvasElement): string {
  const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
  return dataUrl.split(',')[1] ?? '';
}
