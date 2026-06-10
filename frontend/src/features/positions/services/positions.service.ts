import { apiClient } from '@/lib/api/client';
import { ENDPOINTS } from '@/lib/api/endpoints';
import type {
  Position,
  PaginatedPositions,
  PositionCreateDto,
  PositionUpdateDto,
  ListPositionsParams,
} from '../types';

/**
 * Positions API service.
 * Maps directly to backend /api/v1/employees/positions endpoints.
 */
export const positionsService = {
  /**
   * GET /api/v1/employees/positions
   * Paginated list — backend uses offset/limit, not page number.
   */
  list: (params: ListPositionsParams = {}): Promise<PaginatedPositions> =>
    apiClient.get<PaginatedPositions>(ENDPOINTS.POSITIONS, {
      params: {
        offset: params.offset ?? 0,
        limit:  params.limit  ?? 50,
      },
    }),

  /**
   * GET /api/v1/employees/positions/:id
   */
  getById: (id: string): Promise<Position> =>
    apiClient.get<Position>(ENDPOINTS.POSITION(id)),

  /**
   * POST /api/v1/employees/positions
   */
  create: (data: PositionCreateDto): Promise<Position> =>
    apiClient.post<Position>(ENDPOINTS.POSITIONS, data),

  /**
   * PATCH /api/v1/employees/positions/:id
   */
  update: (id: string, data: PositionUpdateDto): Promise<Position> =>
    apiClient.patch<Position>(ENDPOINTS.POSITION(id), data),

  /**
   * DELETE /api/v1/employees/positions/:id  →  204 No Content
   */
  delete: (id: string): Promise<void> =>
    apiClient.delete<void>(ENDPOINTS.POSITION(id)),
};
