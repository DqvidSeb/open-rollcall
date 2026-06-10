'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { X } from '@phosphor-icons/react';
import { Button } from '@/components/ui/Button/Button';
import { ApiError } from '@/lib/api/client';
import { positionsService } from '../services/positions.service';
import { PositionFormFields } from './PositionFormFields';
import { PositionSheetShell } from './PositionSheetShell';

interface CreatePositionSheetProps {
  open: boolean;
  onClose: () => void;
  /** Called after the position was created successfully. */
  onCreated: () => void;
}

const initialState = {
  name:        '',
  description: '',
};

export function CreatePositionSheet({ open, onClose, onCreated }: CreatePositionSheetProps) {
  const t = useTranslations('Positions.form');

  const [form, setForm] = useState(initialState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset the form whenever the sheet is opened.
  useEffect(() => {
    if (!open) return;
    setForm(initialState);
    setError(null);
  }, [open]);

  const update = (field: keyof typeof initialState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await positionsService.create({
        name:        form.name,
        description: form.description || null,
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('errorGeneric'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <PositionSheetShell open={open} onClose={onClose} labelledBy="create-position-title">
        {/* Header */}
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
            <h2 id="create-position-title" style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ct-primary)', letterSpacing: '-0.01em' }}>
              {t('createTitle')}
            </h2>
            <p style={{ fontSize: '12.5px', color: 'var(--ct-secondary)', marginTop: '2px' }}>
              {t('createDescription')}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('cancelButton')}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              width: '32px', height: '32px', borderRadius: '9999px', border: 'none',
              background: 'transparent', color: 'var(--ct-secondary)', cursor: 'pointer',
              transition: 'background 130ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--ac-subtle)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
          >
            <X size={18} weight="bold" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <PositionFormFields
              name={form.name}
              description={form.description}
              onChangeName={update('name')}
              onChangeDescription={update('description')}
              error={error}
              autoFocusName
            />
          </div>

          {/* Footer */}
          <div
            style={{
              display:      'flex',
              justifyContent: 'flex-end',
              gap:          '10px',
              padding:      '16px 24px',
              borderTop:    '1px solid var(--sf-border)',
              flexShrink:   0,
            }}
          >
            <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>
              {t('cancelButton')}
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting}>
              {isSubmitting ? t('submittingButton') : t('submitButton')}
            </Button>
          </div>
        </form>
      </PositionSheetShell>
    </>
  );
}
