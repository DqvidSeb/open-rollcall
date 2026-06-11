/** Mirrors backend app/schemas/attendance.py → AttendanceRead (subset used by the UI). */
export interface AttendanceCheckResult {
  event_type: 'check_in' | 'check_out';
  full_name: string | null;
  person_type: 'employee' | 'student' | null;
  code: string | null;
  confidence: number | null;
  event_time: string;
}

/** Phases of the live recognition loop shown inside the camera modal. */
export type RecognitionPhase =
  | 'requesting-camera'
  | 'scanning'
  | 'recognized'
  | 'no-match'
  | 'blocked'
  | 'error';

/** Transient feedback shown over the video while `phase === 'no-match'`. */
export interface NoMatchInfo {
  message: string;
}
