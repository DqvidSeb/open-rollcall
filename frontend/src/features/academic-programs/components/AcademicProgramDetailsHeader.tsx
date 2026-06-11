'use client';

import { useTranslations } from 'next-intl';
import { X, PencilSimple, Trash } from '@phosphor-icons/react';
import type { AcademicProgram } from '../types';

interface AcademicProgramDetailsHeaderProps {
  program:    AcademicProgram | null;
  isEditing:  boolean;
  onEdit:     () => void;
  onDelete:   () => void;
  onClose:    () => void;
}

const iconButtonStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  width: '32px', height: '32px', borderRadius: '9999px', border: 'none',
  background: 'transparent', cursor: 'pointer',
  transition: 'background 130ms ease',
};

export function AcademicProgramDetailsHeader({ program, isEditing, onEdit, onDelete, onClose }: AcademicProgramDetailsHeaderProps) {
  const t = useTranslations('AcademicPrograms.form');

  return (
    <div
      style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        '20px 24px',
        borderBottom:   '1px solid var(--sf-border)',
        flexShrink:     0,
      }}
    >
      <div>
        <h2 id="academic-program-details-title" style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ct-primary)', letterSpacing: '-0.01em' }}>
          {program?.name ?? t('detailsTitle')}
        </h2>
        <p style={{ fontSize: '12.5px', color: 'var(--ct-secondary)', marginTop: '2px' }}>
          {t('detailsTitle')}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <button
          type="button"
          onClick={onEdit}
          disabled={isEditing}
          aria-label={t('editButton')}
          style={{ ...iconButtonStyle, color: 'var(--ct-secondary)', cursor: isEditing ? 'default' : 'pointer', opacity: isEditing ? 0.4 : 1 }}
          onMouseEnter={e => { if (!isEditing) e.currentTarget.style.background = 'var(--ac-subtle)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
        >
          <PencilSimple size={17} weight="bold" />
        </button>

        <button
          type="button"
          onClick={onDelete}
          aria-label={t('deleteButton')}
          style={{ ...iconButtonStyle, color: '#dc2626' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'rgba(220, 38, 38, 0.10)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
        >
          <Trash size={17} weight="bold" />
        </button>

        <button
          type="button"
          onClick={onClose}
          aria-label={t('cancelButton')}
          style={{ ...iconButtonStyle, color: 'var(--ct-secondary)' }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--ac-subtle)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
        >
          <X size={18} weight="bold" />
        </button>
      </div>
    </div>
  );
}
