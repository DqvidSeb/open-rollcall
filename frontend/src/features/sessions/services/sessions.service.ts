// Sessions service — stub, to be implemented
import type { Session, CreateSessionDto, UpdateSessionDto, SessionFilters } from '../types';
import type { PaginatedResponse } from '@/types/api';

export const sessionsService = {
  list: async (_filters: SessionFilters): Promise<PaginatedResponse<Session>> => {
    // TODO: GET /api/v1/sessions
    throw new Error('Not implemented');
  },

  getById: async (_id: string): Promise<Session> => {
    // TODO: GET /api/v1/sessions/:id
    throw new Error('Not implemented');
  },

  create: async (_data: CreateSessionDto): Promise<Session> => {
    // TODO: POST /api/v1/sessions
    throw new Error('Not implemented');
  },

  update: async (_id: string, _data: UpdateSessionDto): Promise<Session> => {
    // TODO: PATCH /api/v1/sessions/:id
    throw new Error('Not implemented');
  },

  start: async (_id: string): Promise<Session> => {
    // TODO: POST /api/v1/sessions/:id/start
    throw new Error('Not implemented');
  },

  end: async (_id: string): Promise<Session> => {
    // TODO: POST /api/v1/sessions/:id/end
    throw new Error('Not implemented');
  },

  delete: async (_id: string): Promise<void> => {
    // TODO: DELETE /api/v1/sessions/:id
    throw new Error('Not implemented');
  },
};
