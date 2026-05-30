export interface AttendanceReportRow {
  studentId: string;
  studentName: string;
  studentCode: string;
  totalSessions: number;
  present: number;
  absent: number;
  late: number;
  excused: number;
  attendanceRate: number;
}

export interface DailyAttendanceSeries {
  date: string;
  present: number;
  absent: number;
  late: number;
}

export interface ReportFilters {
  courseCode?: string;
  dateFrom?: string;
  dateTo?: string;
  sessionId?: string;
}
