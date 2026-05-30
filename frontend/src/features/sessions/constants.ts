import type { SessionStatus } from './types';
import type { BadgeVariant } from '@/components/ui/Badge';

export const SESSION_STATUS_BADGE: Record<SessionStatus, BadgeVariant> = {
  scheduled: 'info',
  active: 'success',
  completed: 'default',
  cancelled: 'danger',
};

export const SESSIONS_PER_PAGE = 15;
