// Attendance service — stub, to be implemented
import type { AttendanceRecord, AttendanceFilters, AttendanceSummary } from '../types';
import type { PaginatedResponse } from '@/types/api';

export const attendanceService = {
  list: async (_filters: AttendanceFilters): Promise<PaginatedResponse<AttendanceRecord>> => {
    // TODO: GET /api/v1/attendance
    throw new Error('Not implemented');
  },

  getSummary: async (_sessionId: string): Promise<AttendanceSummary> => {
    // TODO: GET /api/v1/attendance/summary?sessionId=...
    throw new Error('Not implemented');
  },

  updateStatus: async (_id: string, _status: string): Promise<AttendanceRecord> => {
    // TODO: PATCH /api/v1/attendance/:id
    throw new Error('Not implemented');
  },

  manualCheckIn: async (_studentId: string, _sessionId: string): Promise<AttendanceRecord> => {
    // TODO: POST /api/v1/attendance/manual-checkin
    throw new Error('Not implemented');
  },
};
