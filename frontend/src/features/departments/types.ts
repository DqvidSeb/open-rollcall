/** Mirrors backend app/schemas/employee.py → DepartmentRead */
export interface Department {
  id: string;           // UUID
  name: string;
  description: string | null;
  created_at: string;   // ISO datetime
  updated_at: string;
}

/** Mirrors PaginatedDepartments */
export interface PaginatedDepartments {
  items: Department[];
  total: number;
  offset: number;
  limit: number;
}

/** Mirrors DepartmentCreate */
export interface DepartmentCreateDto {
  name: string;
  description?: string | null;
}

/** Mirrors DepartmentUpdate */
export interface DepartmentUpdateDto {
  name?: string;
  description?: string | null;
}

export interface ListDepartmentsParams {
  offset?: number;
  limit?: number;
}
