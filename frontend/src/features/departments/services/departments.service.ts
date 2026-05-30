import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type {
  Department,
  PaginatedDepartments,
  DepartmentCreateDto,
  DepartmentUpdateDto,
  ListDepartmentsParams,
} from '../types';

/**
 * Departments API service.
 * Maps directly to backend /api/v1/employees/departments endpoints.
 */
export const departmentsService = {
  /**
   * GET /api/v1/employees/departments
   * Paginated list — backend uses offset/limit, not page number.
   */
  list: (params: ListDepartmentsParams = {}): Promise<PaginatedDepartments> =>
    apiClient.get<PaginatedDepartments>(ENDPOINTS.DEPARTMENTS, {
      params: {
        offset: params.offset ?? 0,
        limit:  params.limit  ?? 50,
      },
    }),

  /**
   * GET /api/v1/employees/departments/:id
   */
  getById: (id: string): Promise<Department> =>
    apiClient.get<Department>(ENDPOINTS.DEPARTMENT(id)),

  /**
   * POST /api/v1/employees/departments
   */
  create: (data: DepartmentCreateDto): Promise<Department> =>
    apiClient.post<Department>(ENDPOINTS.DEPARTMENTS, data),

  /**
   * PATCH /api/v1/employees/departments/:id
   */
  update: (id: string, data: DepartmentUpdateDto): Promise<Department> =>
    apiClient.patch<Department>(ENDPOINTS.DEPARTMENT(id), data),

  /**
   * DELETE /api/v1/employees/departments/:id  →  204 No Content
   */
  delete: (id: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.DEPARTMENT(id)),
};
