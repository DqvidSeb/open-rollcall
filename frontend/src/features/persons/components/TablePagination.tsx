'use client';

import { CaretLeft, CaretRight } from '@phosphor-icons/react';
import { useTranslations } from 'next-intl';

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50, 100] as const;

interface TablePaginationProps {
  page:           number;
  totalPages:     number;
  total:          number;
  limit:          number;
  onPageChange:   (page: number) => void;
  onLimitChange:  (limit: number) => void;
}

const navBtn: React.CSSProperties = {
  display:        'flex',
  alignItems:     'center',
  justifyContent: 'center',
  width:          '30px',
  height:         '30px',
  borderRadius:   '7px',
  border:         'none',
  background:     'transparent',
  color:          'var(--tbl-secondary)',
  cursor:         'pointer',
  transition:     'background 120ms ease, color 120ms ease',
};

export function TablePagination({
  page, totalPages, total, limit, onPageChange, onLimitChange,
}: TablePaginationProps) {
  const t = useTranslations('Persons');

  const onEnter = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.background = 'var(--sb-hover-bg)';
    e.currentTarget.style.color      = 'var(--tbl-primary)';
  };
  const onLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.background = 'transparent';
    e.currentTarget.style.color      = 'var(--tbl-secondary)';
  };

  return (
    <div
      className="flex items-center justify-between"
      style={{ paddingTop: '12px', borderTop: '1px solid var(--tbl-divider)' }}
    >
      {/* Left — page info */}
      <span style={{ fontSize: '12.5px', color: 'var(--tbl-secondary)', letterSpacing: '-0.01em' }}>
        {t('pagination', { page, total: totalPages, count: total })}
      </span>

      {/* Right — nav + rows per page */}
      <div className="flex items-center gap-1">
        {/* Prev */}
        <button
          type="button"
          style={navBtn}
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          onMouseEnter={onEnter}
          onMouseLeave={onLeave}
          aria-label="Previous page"
        >
          <CaretLeft size={14} weight="bold" />
        </button>

        {/* Next */}
        <button
          type="button"
          style={navBtn}
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          onMouseEnter={onEnter}
          onMouseLeave={onLeave}
          aria-label="Next page"
        >
          <CaretRight size={14} weight="bold" />
        </button>

        {/* Rows per page */}
        <select
          value={limit}
          onChange={e => { onLimitChange(Number(e.target.value)); onPageChange(1); }}
          aria-label="Rows per page"
          style={{
            marginLeft:   '8px',
            padding:      '4px 8px',
            borderRadius: '7px',
            border:       '1px solid var(--tbl-divider)',
            background:   'transparent',
            color:        'var(--tbl-secondary)',
            fontSize:     '12.5px',
            cursor:       'pointer',
            outline:      'none',
          }}
        >
          {PAGE_SIZE_OPTIONS.map(n => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
