// SessionCard — stub, to be implemented
'use client';

import type { Session } from '../types';

interface SessionCardProps {
  session: Session;
  onStart?: (id: string) => void;
  onEnd?: (id: string) => void;
  onEdit?: (session: Session) => void;
}

export function SessionCard(_props: SessionCardProps) {
  // TODO: show name, date, status badge, attendance count, actions
  return null;
}
