/** Mirrors backend app/schemas/employee.py → PositionRead */
export interface Position {
  id: string;           // UUID
  name: string;
  description: string | null;
  created_at: string;   // ISO datetime
  updated_at: string;
}

/** Mirrors PaginatedPositions */
export interface PaginatedPositions {
  items: Position[];
  total: number;
  offset: number;
  limit: number;
}

/** Mirrors PositionCreate */
export interface PositionCreateDto {
  name: string;
  description?: string | null;
}

/** Mirrors PositionUpdate */
export interface PositionUpdateDto {
  name?: string;
  description?: string | null;
}

export interface ListPositionsParams {
  offset?: number;
  limit?: number;
}
