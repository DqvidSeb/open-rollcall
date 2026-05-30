// All backend endpoint paths — single source of truth
export const ENDPOINTS = {
  // ── Departments (/api/v1/employees/departments) ──────────────────────────
  DEPARTMENTS:     '/api/v1/employees/departments',
  DEPARTMENT:      (id: string) => `/api/v1/employees/departments/${id}`,

  // ── Positions (/api/v1/employees/positions) ──────────────────────────────
  POSITIONS:       '/api/v1/employees/positions',
  POSITION:        (id: string) => `/api/v1/employees/positions/${id}`,

  // ── Employees (/api/v1/employees) ────────────────────────────────────────
  EMPLOYEES:       '/api/v1/employees',
  EMPLOYEE:        (id: string) => `/api/v1/employees/${id}`,

  // Auth
  AUTH_LOGIN: '/api/v1/auth/login',
  AUTH_REGISTER: '/api/v1/auth/register',
  AUTH_LOGOUT: '/api/v1/auth/logout',
  AUTH_REFRESH: '/api/v1/auth/refresh',
  AUTH_ME: '/api/v1/auth/me',

  // Students
  STUDENTS: '/api/v1/students',
  STUDENT: (id: string) => `/api/v1/students/${id}`,
  STUDENT_FACE: (id: string) => `/api/v1/students/${id}/face`,

  // Sessions
  SESSIONS: '/api/v1/sessions',
  SESSION: (id: string) => `/api/v1/sessions/${id}`,
  SESSION_START: (id: string) => `/api/v1/sessions/${id}/start`,
  SESSION_END: (id: string) => `/api/v1/sessions/${id}/end`,

  // Attendance
  ATTENDANCE: '/api/v1/attendance',
  ATTENDANCE_SUMMARY: '/api/v1/attendance/summary',
  ATTENDANCE_MANUAL_CHECKIN: '/api/v1/attendance/manual-checkin',

  // Recognition
  RECOGNITION_RECOGNIZE: '/api/v1/recognition/recognize',
  RECOGNITION_CHECKIN: '/api/v1/recognition/checkin',
  RECOGNITION_CHECKOUT: '/api/v1/recognition/checkout',

  // Reports
  REPORTS_ATTENDANCE: '/api/v1/reports/attendance',
  REPORTS_DAILY_SERIES: '/api/v1/reports/daily-series',
  REPORTS_EXPORT: '/api/v1/reports/export',
} as const;
