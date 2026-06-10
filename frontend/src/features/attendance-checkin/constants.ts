/**
 * Tuning constants for the live check-in/check-out recognition loop.
 *
 * Mirrors the timing of the backend's `camera_client.py attend` script:
 * frames are sent at a steady pace, a successful match is held on screen
 * for a few seconds (matching the server's overlay duration), and brief
 * "no match" feedback fades quickly so the loop keeps scanning.
 */

/** Delay (ms) between frames sent to the recognition endpoint while scanning. */
export const RECOGNITION_INTERVAL_MS = 1200;

/** How long a successful recognition stays on screen before resuming scanning (ms). */
export const SUCCESS_DISPLAY_MS = 5500;

/** How long a transient "not recognized" hint stays on screen (ms). */
export const NO_MATCH_DISPLAY_MS = 1600;

/** How long a "already registered today" conflict message stays on screen (ms). */
export const CONFLICT_DISPLAY_MS = 3000;

/** Width (px) of the wide frame sent to the backend. */
export const CAPTURE_WIDTH = 640;

/** Height (px) of the wide frame sent to the backend (16:9). */
export const CAPTURE_HEIGHT = 360;

/** JPEG quality used when encoding captured frames. */
export const JPEG_QUALITY = 0.85;
