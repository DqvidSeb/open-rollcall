import { MAX_BRIGHTNESS, MIN_BRIGHTNESS, MIN_SHARPNESS } from '../constants';

export interface QualityResult {
  ok: boolean;
  brightness: number;
  sharpness: number;
  /** Translation key suffix describing why the frame was rejected, if any. */
  reasonKey: 'tooDark' | 'tooBright' | 'tooBlurry' | null;
}

/**
 * Downscales the given canvas to a small grayscale buffer and computes:
 * - mean brightness (0-255)
 * - sharpness via Laplacian variance (higher = sharper)
 *
 * This is a lightweight client-side sanity check — the backend (DeepFace)
 * performs the real face detection and alignment.
 */
export function evaluateFrameQuality(source: HTMLCanvasElement): QualityResult {
  const sampleSize = 96;
  const canvas = document.createElement('canvas');
  canvas.width = sampleSize;
  canvas.height = sampleSize;

  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  if (!ctx) {
    return { ok: true, brightness: 128, sharpness: MIN_SHARPNESS, reasonKey: null };
  }

  ctx.drawImage(source, 0, 0, sampleSize, sampleSize);
  const { data } = ctx.getImageData(0, 0, sampleSize, sampleSize);

  const gray = new Float32Array(sampleSize * sampleSize);
  let sum = 0;
  for (let i = 0, p = 0; i < data.length; i += 4, p++) {
    const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
    gray[p] = lum;
    sum += lum;
  }
  const brightness = sum / gray.length;
  const sharpness = laplacianVariance(gray, sampleSize, sampleSize);

  let reasonKey: QualityResult['reasonKey'] = null;
  if (brightness < MIN_BRIGHTNESS) reasonKey = 'tooDark';
  else if (brightness > MAX_BRIGHTNESS) reasonKey = 'tooBright';
  else if (sharpness < MIN_SHARPNESS) reasonKey = 'tooBlurry';

  return { ok: reasonKey === null, brightness, sharpness, reasonKey };
}

/** Variance of the 4-neighbor Laplacian — a common blur detection metric. */
function laplacianVariance(gray: Float32Array, width: number, height: number): number {
  const lap: number[] = [];
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      const value =
        4 * gray[idx]
        - gray[idx - 1] - gray[idx + 1]
        - gray[idx - width] - gray[idx + width];
      lap.push(value);
    }
  }
  const mean = lap.reduce((a, b) => a + b, 0) / lap.length;
  const variance = lap.reduce((a, b) => a + (b - mean) ** 2, 0) / lap.length;
  return variance;
}
