// Students service — stub, to be implemented
import type { Student, CreateStudentDto, UpdateStudentDto, StudentFilters } from '../types';
import type { PaginatedResponse } from '@/types/api';

export const studentsService = {
  list: async (_filters: StudentFilters): Promise<PaginatedResponse<Student>> => {
    // TODO: GET /api/v1/students
    throw new Error('Not implemented');
  },

  getById: async (_id: string): Promise<Student> => {
    // TODO: GET /api/v1/students/:id
    throw new Error('Not implemented');
  },

  create: async (_data: CreateStudentDto): Promise<Student> => {
    // TODO: POST /api/v1/students
    throw new Error('Not implemented');
  },

  update: async (_id: string, _data: UpdateStudentDto): Promise<Student> => {
    // TODO: PATCH /api/v1/students/:id
    throw new Error('Not implemented');
  },

  delete: async (_id: string): Promise<void> => {
    // TODO: DELETE /api/v1/students/:id
    throw new Error('Not implemented');
  },

  uploadFacePhoto: async (_id: string, _file: File): Promise<Student> => {
    // TODO: POST /api/v1/students/:id/face
    throw new Error('Not implemented');
  },
};
