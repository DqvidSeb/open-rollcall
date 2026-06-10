/** Mirrors backend app/schemas/person.py → PersonListItem */
export type PersonType = 'employee' | 'student';

export interface Person {
  id: string;          // UUID
  full_name: string;
  email: string | null;
  phone: string | null;
  person_type: PersonType | null;
  code: string | null;
  group_name: string | null;
  status: string | null;
  created_at: string;  // ISO datetime
}

/** Mirrors PaginatedPersons */
export interface PaginatedPersons {
  items: Person[];
  total: number;
  offset: number;
  limit: number;
}

export interface ListPersonsParams {
  offset?: number;
  limit?: number;
}

/** Mirrors backend app/schemas/employee.py → EmployeeStatus */
export type EmployeeStatus = 'active' | 'inactive' | 'on_leave';

/** Mirrors backend app/schemas/student.py → StudentStatus */
export type StudentStatus = 'active' | 'inactive' | 'graduated' | 'suspended';

/** Mirrors EmployeeCreate */
export interface EmployeeCreateDto {
  first_name: string;
  last_name: string;
  email?: string | null;
  phone?: string | null;
  employee_code: string;
  department_id?: string | null;
  position_id?: string | null;
  status?: EmployeeStatus;
  hire_date?: string | null;
}

/** Mirrors StudentCreate */
export interface StudentCreateDto {
  first_name: string;
  last_name: string;
  email?: string | null;
  phone?: string | null;
  student_code: string;
  academic_program_id?: string | null;
  grade_level?: string | null;
  status?: StudentStatus;
  enrollment_date?: string | null;
}

/** Lightweight option shapes for select inputs */
export interface OptionItem {
  id: string;
  name: string;
}

/** Mirrors backend app/schemas/person.py → PersonRead */
export interface PersonDetail {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string | null;
  phone: string | null;
}

/** Mirrors PersonUpdate */
export interface PersonUpdateDto {
  first_name?: string;
  last_name?: string;
  email?: string | null;
  phone?: string | null;
}

/** Mirrors backend app/schemas/employee.py → EmployeeRead */
export interface EmployeeDetail {
  id: string;
  employee_code: string;
  department_id: string | null;
  position_id: string | null;
  status: EmployeeStatus;
  hire_date: string | null;
}

/** Mirrors EmployeeUpdate (excludes employee_code — immutable) */
export interface EmployeeUpdateDto {
  first_name?: string;
  last_name?: string;
  email?: string | null;
  phone?: string | null;
  department_id?: string | null;
  position_id?: string | null;
  status?: EmployeeStatus;
  hire_date?: string | null;
}

/** Mirrors backend app/schemas/student.py → StudentRead */
export interface StudentDetail {
  id: string;
  student_code: string;
  academic_program_id: string | null;
  grade_level: string | null;
  status: StudentStatus;
  enrollment_date: string | null;
}

/** Mirrors StudentUpdate (excludes student_code — immutable) */
export interface StudentUpdateDto {
  first_name?: string;
  last_name?: string;
  email?: string | null;
  phone?: string | null;
  academic_program_id?: string | null;
  grade_level?: string | null;
  status?: StudentStatus;
  enrollment_date?: string | null;
}
