import { clsx } from 'clsx';

interface TableProps {
  children: React.ReactNode;
  className?: string;
}

interface TableHeadProps {
  children: React.ReactNode;
}

interface TableBodyProps {
  children: React.ReactNode;
}

interface TableRowProps {
  children: React.ReactNode;
  onClick?: () => void;
  isClickable?: boolean;
}

interface TableCellProps {
  children: React.ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right';
}

interface TableHeaderCellProps extends TableCellProps {
  sortable?: boolean;
  sorted?: 'asc' | 'desc' | null;
  onSort?: () => void;
}

export function Table({ children, className }: TableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className={clsx('min-w-full divide-y divide-gray-200', className)}>
        {children}
      </table>
    </div>
  );
}

export function TableHead({ children }: TableHeadProps) {
  return <thead className="bg-gray-50">{children}</thead>;
}

export function TableBody({ children }: TableBodyProps) {
  return <tbody className="bg-white divide-y divide-gray-100">{children}</tbody>;
}

export function TableRow({ children, onClick, isClickable = false }: TableRowProps) {
  return (
    <tr
      onClick={onClick}
      className={clsx(isClickable && 'cursor-pointer hover:bg-gray-50 transition-colors')}
    >
      {children}
    </tr>
  );
}

export function TableHeaderCell({ children, className, align = 'left', sortable, sorted, onSort }: TableHeaderCellProps) {
  return (
    <th
      scope="col"
      onClick={sortable ? onSort : undefined}
      className={clsx(
        'px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider',
        `text-${align}`,
        sortable && 'cursor-pointer select-none hover:text-gray-700',
        className,
      )}
    >
      <span className="inline-flex items-center gap-1">
        {children}
        {sortable && sorted === 'asc' && '↑'}
        {sortable && sorted === 'desc' && '↓'}
      </span>
    </th>
  );
}

export function TableCell({ children, className, align = 'left' }: TableCellProps) {
  return (
    <td className={clsx('px-4 py-3 text-sm text-gray-700', `text-${align}`, className)}>
      {children}
    </td>
  );
}
