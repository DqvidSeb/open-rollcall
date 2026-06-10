import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type {
  PaginatedPersons, ListPersonsParams,
  EmployeeCreateDto, StudentCreateDto, OptionItem,
  PersonDetail, PersonUpdateDto,
  EmployeeDetail, EmployeeUpdateDto,
  StudentDetail, StudentUpdateDto,
} from '../types';

interface PaginatedItems<T> {
  items: T[];
}

/**
 * Persons API service.
 * Maps directly to the backend /api/v1/persons endpoints.
 */
export const personsService = {
  /**
   * GET /api/v1/persons
   * Paginated list — backend uses offset/limit, not page number.
   */
  list: (params: ListPersonsParams = {}): Promise<PaginatedPersons> =>
    apiClient.get<PaginatedPersons>(ENDPOINTS.PERSONS, {
      params: {
        offset: params.offset ?? 0,
        limit:  params.limit  ?? 50,
      },
    }),

  /**
   * POST /api/v1/employees
   * Creates a Person + Employee record.
   */
  createEmployee: (data: EmployeeCreateDto) =>
    apiClient.post(ENDPOINTS.EMPLOYEES, data),

  /**
   * POST /api/v1/students
   * Creates a Person + Student record.
   */
  createStudent: (data: StudentCreateDto) =>
    apiClient.post(ENDPOINTS.STUDENTS, data),

  /** GET /api/v1/employees/departments — for the department select */
  listDepartments: async (): Promise<OptionItem[]> => {
    const res = await apiClient.get<PaginatedItems<OptionItem>>(ENDPOINTS.DEPARTMENTS, {
      params: { limit: 200 },
    });
    return res.items;
  },

  /** GET /api/v1/employees/positions — for the position select */
  listPositions: async (): Promise<OptionItem[]> => {
    const res = await apiClient.get<PaginatedItems<OptionItem>>(ENDPOINTS.POSITIONS, {
      params: { limit: 200 },
    });
    return res.items;
  },

  /** GET /api/v1/students/programs — for the academic program select */
  listAcademicPrograms: async (): Promise<OptionItem[]> => {
    const res = await apiClient.get<PaginatedItems<OptionItem>>(ENDPOINTS.ACADEMIC_PROGRAMS, {
      params: { limit: 200 },
    });
    return res.items;
  },

  /** GET /api/v1/persons/:id — base person fields (name, email, phone) */
  getPerson: (id: string): Promise<PersonDetail> =>
    apiClient.get<PersonDetail>(ENDPOINTS.PERSON(id)),

  /** PATCH /api/v1/persons/:id */
  updatePerson: (id: string, data: PersonUpdateDto): Promise<PersonDetail> =>
    apiClient.patch<PersonDetail>(ENDPOINTS.PERSON(id), data),

  /** GET /api/v1/employees/:id */
  getEmployee: (id: string): Promise<EmployeeDetail> =>
    apiClient.get<EmployeeDetail>(ENDPOINTS.EMPLOYEE(id)),

  /** PATCH /api/v1/employees/:id */
  updateEmployee: (id: string, data: EmployeeUpdateDto): Promise<EmployeeDetail> =>
    apiClient.patch<EmployeeDetail>(ENDPOINTS.EMPLOYEE(id), data),

  /** DELETE /api/v1/employees/:id — soft delete */
  deleteEmployee: (id: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.EMPLOYEE(id)),

  /** GET /api/v1/students/:id */
  getStudent: (id: string): Promise<StudentDetail> =>
    apiClient.get<StudentDetail>(ENDPOINTS.STUDENT(id)),

  /** PATCH /api/v1/students/:id */
  updateStudent: (id: string, data: StudentUpdateDto): Promise<StudentDetail> =>
    apiClient.patch<StudentDetail>(ENDPOINTS.STUDENT(id), data),

  /** DELETE /api/v1/students/:id — soft delete */
  deleteStudent: (id: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.STUDENT(id)),
};
