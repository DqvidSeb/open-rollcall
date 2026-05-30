export type AttendanceStatus = 'present' | 'absent' | 'late' | 'excused';

export interface AttendanceRecord {
  id: string;
  studentId: string;
  sessionId: string;
  status: AttendanceStatus;
  checkInAt?: string | null;
  checkOutAt?: string | null;
  confidence?: number | null;
  detectedByFace: boolean;
  notes?: string | null;
  createdAt: string;
}

export interface AttendanceFilters {
  sessionId?: string;
  studentId?: string;
  status?: AttendanceStatus;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  limit?: number;
}

export interface AttendanceSummary {
  total: number;
  present: number;
  absent: number;
  late: number;
  excused: number;
  attendanceRate: number;
}
