// StudentCard — stub, to be implemented
'use client';

import type { Student } from '../types';

interface StudentCardProps {
  student: Student;
  onEdit?: (student: Student) => void;
  onDelete?: (id: string) => void;
}

export function StudentCard(_props: StudentCardProps) {
  // TODO: implement card with avatar, name, code, enrollment badge
  return null;
}
