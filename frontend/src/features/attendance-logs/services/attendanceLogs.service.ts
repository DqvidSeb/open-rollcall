import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type { PaginatedAttendanceLogs, ListAttendanceLogsParams } from '../types';

/**
 * Attendance logs API service.
 * Maps directly to the backend GET /api/v1/attendance endpoint.
 */
export const attendanceLogsService = {
  /**
   * GET /api/v1/attendance
   * Paginated list of attendance records (most recent first).
   */
  list: (params: ListAttendanceLogsParams = {}): Promise<PaginatedAttendanceLogs> =>
    apiClient.get<PaginatedAttendanceLogs>(ENDPOINTS.ATTENDANCE, {
      params: {
        page: params.page ?? 1,
        page_size: params.page_size ?? 50,
      },
    }),
};
