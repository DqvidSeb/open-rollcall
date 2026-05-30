import type { AttendanceStatus } from './types';
import type { BadgeVariant } from '@/components/ui/Badge';

export const ATTENDANCE_STATUS_BADGE: Record<AttendanceStatus, BadgeVariant> = {
  present: 'success',
  absent: 'danger',
  late: 'warning',
  excused: 'info',
};

export const ATTENDANCE_PER_PAGE = 25;
