// StudentForm — stub, to be implemented (create & edit)
'use client';

import type { Student } from '../types';

interface StudentFormProps {
  student?: Student;
  onSuccess?: (student: Student) => void;
  onCancel?: () => void;
}

export function StudentForm(_props: StudentFormProps) {
  // TODO: implement with react-hook-form + zod
  return null;
}
