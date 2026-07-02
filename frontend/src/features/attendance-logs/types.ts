/** Mirrors backend app/models/attendance_log.py → EventType */
export type AttendanceEventType = 'check_in' | 'check_out';

/** Mirrors backend app/models/attendance_log.py → AttendanceMethod */
export type AttendanceMethod = 'face_recognition' | 'manual' | 'override';

/** Mirrors backend app/schemas/face.py → PersonType */
export type AttendancePersonType = 'employee' | 'student';

/** Mirrors backend app/schemas/attendance.py → AttendanceRead */
export interface AttendanceLogItem {
  id: string;
  event_type: AttendanceEventType;
  method: AttendanceMethod;
  event_time: string; // ISO datetime
  confidence: number | null;
  notes: string | null;

  person_id: string;
  person_type: AttendancePersonType | null;
  code: string | null;
  full_name: string | null;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;

  department: string | null;
  position: string | null;
  status: string | null;
  hire_date: string | null;

  academic_program: string | null;
  grade_level: string | null;
  enrollment_date: string | null;
}

/** Mirrors backend app/schemas/attendance.py → PaginatedAttendance */
export interface PaginatedAttendanceLogs {
  items: AttendanceLogItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ListAttendanceLogsParams {
  /** 1-based page number */
  page?: number;
  page_size?: number;
}
