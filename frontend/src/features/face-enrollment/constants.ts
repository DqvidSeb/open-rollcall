/**
 * Tuning constants for the guided facial enrollment flow.
 *
 * Mirrors the structure of the backend's `camera_client.py enroll` script
 * (5 angles, positioning delay, per-photo confirmation), adapted for the
 * browser where the server (DeepFace + RetinaFace) handles face detection
 * and alignment — the client only needs to guide framing and check basic
 * frame quality.
 */

export const TOTAL_SAMPLES = 5;

/** Seconds the user has to position their face before the first capture. */
export const POSITIONING_SECONDS = 6;

/** Seconds between each subsequent capture. */
export const BETWEEN_CAPTURE_SECONDS = 5;

/** How long the "photo captured" confirmation overlay stays visible (ms). */
export const CONFIRMATION_DISPLAY_MS = 1400;

/** Side length (px) of the square frame sent to the backend. */
export const CAPTURE_SIZE = 480;

/** JPEG quality used when encoding captured frames. */
export const JPEG_QUALITY = 0.9;

/** Minimum acceptable mean brightness (0-255). */
export const MIN_BRIGHTNESS = 40;

/** Maximum acceptable mean brightness (0-255). */
export const MAX_BRIGHTNESS = 240;

/** Minimum acceptable sharpness score (Laplacian variance, downscaled frame). */
export const MIN_SHARPNESS = 12;

/**
 * One instruction per capture, translated via `Persons.form.face.steps.<key>`.
 * The order matches the backend script's angle sequence.
 */
export const CAPTURE_STEP_KEYS = [
  'center',
  'left',
  'right',
  'up',
  'down',
] as const;
