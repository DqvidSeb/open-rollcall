// Reports service — stub, to be implemented
import type { AttendanceReportRow, DailyAttendanceSeries, ReportFilters } from '../types';

export const reportsService = {
  getAttendanceReport: async (_filters: ReportFilters): Promise<AttendanceReportRow[]> => {
    // TODO: GET /api/v1/reports/attendance
    throw new Error('Not implemented');
  },

  getDailySeries: async (_filters: ReportFilters): Promise<DailyAttendanceSeries[]> => {
    // TODO: GET /api/v1/reports/daily-series
    throw new Error('Not implemented');
  },

  exportCsv: async (_filters: ReportFilters): Promise<Blob> => {
    // TODO: GET /api/v1/reports/export?format=csv
    throw new Error('Not implemented');
  },
};
