// SessionForm — stub, to be implemented (create & edit)
'use client';

import type { Session } from '../types';

interface SessionFormProps {
  session?: Session;
  onSuccess?: (session: Session) => void;
  onCancel?: () => void;
}

export function SessionForm(_props: SessionFormProps) {
  // TODO: implement with react-hook-form + zod
  return null;
}
