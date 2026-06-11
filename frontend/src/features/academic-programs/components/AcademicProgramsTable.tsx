'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useAcademicPrograms } from '../hooks/useAcademicPrograms';
import { AcademicProgramRow } from './AcademicProgramRow';
import { TablePagination } from './TablePagination';
import type { AcademicProgram } from '../types';

interface AcademicProgramsTableProps {
  onRowClick?: (program: AcademicProgram) => void;
}

export function AcademicProgramsTable({ onRowClick }: AcademicProgramsTableProps) {
  const t = useTranslations('AcademicPrograms');

  const [page,       setPage]       = useState(1);
  const [limit,      setLimit]      = useState(10);
  const [selected,   setSelected]   = useState<Set<string>>(new Set());

  const { data, isLoading, error } = useAcademicPrograms({ page, limit });

  const items      = data?.items ?? [];
  const total      = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  // ── Selection handlers ──────────────────────────────────────────────
  const toggleRow = (id: string, checked: boolean) => {
    setSelected(prev => {
      const next = new Set(prev);
      if (checked) next.add(id); else next.delete(id);
      return next;
    });
  };

  const allChecked  = items.length > 0 && items.every(p => selected.has(p.id));
  const someChecked = items.some(p => selected.has(p.id)) && !allChecked;

  const toggleAll = () => {
    if (allChecked) {
      setSelected(prev => { const n = new Set(prev); items.forEach(p => n.delete(p.id)); return n; });
    } else {
      setSelected(prev => { const n = new Set(prev); items.forEach(p => n.add(p.id)); return n; });
    }
  };

  // ── States ──────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', paddingTop: '64px' }}>
        <span style={{
          width: '28px', height: '28px', borderRadius: '50%',
          border: '2.5px solid var(--rc-accent)',
          borderTopColor: 'transparent',
          display: 'inline-block', animation: 'spin 0.7s linear infinite',
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <p style={{ color: 'var(--tbl-secondary)', fontSize: '13.5px', paddingTop: '32px', textAlign: 'center' }}>
        {error}
      </p>
    );
  }

  if (items.length === 0) {
    return (
      <div style={{ textAlign: 'center', paddingTop: '64px' }}>
        <p style={{ color: 'var(--tbl-primary)', fontWeight: 500, marginBottom: '6px' }}>{t('emptyTitle')}</p>
        <p style={{ color: 'var(--tbl-secondary)', fontSize: '13px' }}>{t('emptyDescription')}</p>
      </div>
    );
  }

  return (
    <div>
      <table className="rc-table">
        <thead>
          <tr>
            <th>
              {/* Select-all checkbox */}
              <button
                type="button"
                role="checkbox"
                aria-checked={allChecked ? true : someChecked ? 'mixed' : false}
                onClick={toggleAll}
                style={{
                  width: '17px', height: '17px', borderRadius: '5px',
                  border: allChecked ? 'none' : '1.5px solid var(--tbl-check-border)',
                  background: allChecked ? 'var(--rc-accent)' : 'transparent',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >
                {allChecked && (
                  <svg width="10" height="8" viewBox="0 0 10 8" fill="none"><path d="M1 4L3.8 7L9 1" stroke="var(--rc-ink)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>
                )}
                {someChecked && !allChecked && (
                  <svg width="8" height="2" viewBox="0 0 8 2" fill="none"><path d="M1 1H7" stroke="var(--tbl-header)" strokeWidth="1.8" strokeLinecap="round"/></svg>
                )}
              </button>
            </th>
            <th>{t('colName')}</th>
            <th>{t('colDescription')}</th>
            <th>{t('colCreated')}</th>
            <th>{t('colUpdated')}</th>
          </tr>
        </thead>
        <tbody>
          {items.map(program => (
            <AcademicProgramRow
              key={program.id}
              program={program}
              selected={selected.has(program.id)}
              onSelect={toggleRow}
              onClick={onRowClick ?? (() => {})}
            />
          ))}
        </tbody>
      </table>

      <TablePagination
        page={page}
        totalPages={totalPages}
        total={total}
        limit={limit}
        onPageChange={setPage}
        onLimitChange={setLimit}
      />
    </div>
  );
}
