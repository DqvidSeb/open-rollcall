'use client';

import { AttendanceToolbar } from './AttendanceToolbar';
import { AttendanceTable } from './AttendanceTable';

/**
 * Client-side shell for the Attendance page.
 *
 * Mirrors PersonsPageContent — toolbar + table, no card wrappers.
 */
export function AttendancePageContent() {
  return (
    <div className="flex flex-col gap-5">
      <AttendanceToolbar />
      <AttendanceTable />
    </div>
  );
}
