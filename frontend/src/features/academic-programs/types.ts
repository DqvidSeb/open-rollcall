/** Mirrors backend app/schemas/student.py → AcademicProgramRead */
export interface AcademicProgram {
  id: string;           // UUID
  name: string;
  description: string | null;
  created_at: string;   // ISO datetime
  updated_at: string;
}

/** Mirrors PaginatedAcademicPrograms */
export interface PaginatedAcademicPrograms {
  items: AcademicProgram[];
  total: number;
  offset: number;
  limit: number;
}

/** Mirrors AcademicProgramCreate */
export interface AcademicProgramCreateDto {
  name: string;
  description?: string | null;
}

/** Mirrors AcademicProgramUpdate */
export interface AcademicProgramUpdateDto {
  name?: string;
  description?: string | null;
}

export interface ListAcademicProgramsParams {
  offset?: number;
  limit?: number;
}
