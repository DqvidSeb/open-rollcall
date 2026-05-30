// Shared API response shapes (mirrors FastAPI backend)

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ApiError {
  statusCode: number;
  message: string;
  detail?: string | Record<string, string[]>;
}

export interface ApiSuccessResponse<T = void> {
  data: T;
  message?: string;
}
