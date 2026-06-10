'use client';

import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button/Button';

interface DeleteConfirmModalProps {
  open: boolean;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

/**
 * Minimal centered confirmation modal for deleting a position.
 * No subject details are shown — title + short prompt only.
 */
export function DeleteConfirmModal({ open, isDeleting, onCancel, onConfirm }: DeleteConfirmModalProps) {
  const t = useTranslations('Positions.form');

  if (!open) return null;

  return (
    <>
      <div
        onClick={onCancel}
        style={{
          position:   'fixed',
          inset:      0,
          background: 'rgba(0, 0, 0, 0.45)',
          zIndex:     60,
        }}
        aria-hidden="true"
      />

      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-confirm-title"
        style={{
          position:     'fixed',
          top:          '50%',
          left:         '50%',
          transform:    'translate(-50%, -50%)',
          width:        'min(360px, calc(100vw - 32px))',
          background:   'var(--sf-raised)',
          borderRadius: '10px',
          boxShadow:    '0 12px 40px rgba(0, 0, 0, 0.25)',
          padding:      '22px',
          zIndex:       61,
          display:      'flex',
          flexDirection: 'column',
          gap:          '18px',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <h2 id="delete-confirm-title" style={{ fontSize: '15.5px', fontWeight: 600, color: 'var(--ct-primary)' }}>
            {t('deleteConfirmTitle')}
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--ct-secondary)' }}>
            {t('deleteConfirmText')}
          </p>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <Button type="button" variant="secondary" onClick={onCancel} disabled={isDeleting}>
            {t('cancelButton')}
          </Button>
          <Button type="button" variant="danger" onClick={onConfirm} isLoading={isDeleting}>
            {t('deleteConfirmButton')}
          </Button>
        </div>
      </div>
    </>
  );
}
