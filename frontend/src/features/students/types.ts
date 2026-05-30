export interface Student {
  id: string;
  fullName: string;
  studentCode: string;
  email?: string | null;
  avatarUrl?: string | null;
  faceEmbedding?: number[] | null;
  isEnrolled: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateStudentDto {
  fullName: string;
  studentCode: string;
  email?: string;
}

export interface UpdateStudentDto {
  fullName?: string;
  studentCode?: string;
  email?: string;
}

export interface StudentFilters {
  search?: string;
  isEnrolled?: boolean;
  page?: number;
  limit?: number;
}
