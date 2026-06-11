import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type {
  AcademicProgram,
  PaginatedAcademicPrograms,
  AcademicProgramCreateDto,
  AcademicProgramUpdateDto,
  ListAcademicProgramsParams,
} from '../types';

/**
 * Academic programs API service.
 * Maps directly to backend /api/v1/students/programs endpoints.
 */
export const academicProgramsService = {
  /**
   * GET /api/v1/students/programs
   * Paginated list — backend uses offset/limit, not page number.
   */
  list: (params: ListAcademicProgramsParams = {}): Promise<PaginatedAcademicPrograms> =>
    apiClient.get<PaginatedAcademicPrograms>(ENDPOINTS.ACADEMIC_PROGRAMS, {
      params: {
        offset: params.offset ?? 0,
        limit:  params.limit  ?? 50,
      },
    }),

  /**
   * GET /api/v1/students/programs/:id
   */
  getById: (id: string): Promise<AcademicProgram> =>
    apiClient.get<AcademicProgram>(ENDPOINTS.ACADEMIC_PROGRAM(id)),

  /**
   * POST /api/v1/students/programs
   */
  create: (data: AcademicProgramCreateDto): Promise<AcademicProgram> =>
    apiClient.post<AcademicProgram>(ENDPOINTS.ACADEMIC_PROGRAMS, data),

  /**
   * PATCH /api/v1/students/programs/:id
   */
  update: (id: string, data: AcademicProgramUpdateDto): Promise<AcademicProgram> =>
    apiClient.patch<AcademicProgram>(ENDPOINTS.ACADEMIC_PROGRAM(id), data),

  /**
   * DELETE /api/v1/students/programs/:id  →  204 No Content
   */
  delete: (id: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.ACADEMIC_PROGRAM(id)),
};
