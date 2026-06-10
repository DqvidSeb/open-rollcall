'use client';

import { Plus } from '@phosphor-icons/react';
import { useTranslations } from 'next-intl';

interface DepartmentsToolbarProps {
  /** Called when the "New department" button is clicked */
  onAdd?: () => void;
}

export function DepartmentsToolbar({ onAdd }: DepartmentsToolbarProps) {
  const t = useTranslations('Departments');

  return (
    // No background, no border — visually sits on the page surface
    <div className="flex items-center justify-between">
      <h1 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--tbl-primary)', letterSpacing: '-0.01em' }}>
        {t('title')}
      </h1>

      <button
        type="button"
        onClick={onAdd}
        style={{
          display:        'flex',
          alignItems:     'center',
          gap:            '7px',
          padding:        '9px 18px',
          borderRadius:   '9999px',
          border:         'none',
          cursor:         'pointer',
          background:     'var(--rc-accent)',
          color:          'var(--rc-ink)',
          fontSize:       '13.5px',
          fontWeight:     600,
          letterSpacing:  '-0.01em',
          transition:     'background 130ms ease, transform 80ms ease',
          userSelect:     'none',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = '#e85c1a'; }}
        onMouseLeave={e => { e.currentTarget.style.background = 'var(--rc-accent)'; }}
        onMouseDown={e  => { e.currentTarget.style.transform  = 'scale(0.97)'; }}
        onMouseUp={e    => { e.currentTarget.style.transform  = 'scale(1)'; }}
      >
        <Plus size={15} weight="bold" aria-hidden="true" />
        {t('addButton')}
      </button>
    </div>
  );
}
