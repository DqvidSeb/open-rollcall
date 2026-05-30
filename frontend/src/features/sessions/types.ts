export type SessionStatus = 'scheduled' | 'active' | 'completed' | 'cancelled';

export interface Session {
  id: string;
  name: string;
  description?: string | null;
  courseCode?: string | null;
  instructorId: string;
  scheduledAt: string;
  startedAt?: string | null;
  endedAt?: string | null;
  status: SessionStatus;
  totalStudents: number;
  presentCount: number;
  createdAt: string;
}

export interface CreateSessionDto {
  name: string;
  description?: string;
  courseCode?: string;
  scheduledAt: string;
}

export interface UpdateSessionDto {
  name?: string;
  description?: string;
  courseCode?: string;
  scheduledAt?: string;
}

export interface SessionFilters {
  status?: SessionStatus;
  search?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  limit?: number;
}
