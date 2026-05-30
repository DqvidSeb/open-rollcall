// Global common types

export type Locale = 'en' | 'es';

export type SortDirection = 'asc' | 'desc';

export interface SortState {
  field: string;
  direction: SortDirection;
}

export type Nullable<T> = T | null;

export type Optional<T> = T | undefined;

// Helper for component children with optional className
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}
