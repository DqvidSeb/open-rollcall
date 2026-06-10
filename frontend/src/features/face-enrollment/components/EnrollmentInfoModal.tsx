'use client';

import { createPortal } from 'react-dom';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button/Button';
import { ScanFrameIllustration } from './ScanFrameIllustration';

interface EnrollmentInfoModalProps {
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

const TIP_KEYS = ['lighting', 'noAccessories', 'centerFace'] as const;

/**
 * Centered tutorial/confirmation modal shown before opening the camera.
 * Rendered via a portal so it overlays the whole screen, not just the
 * details sheet (the sheet's `transform` would otherwise re-anchor it).
 */
export function EnrollmentInfoModal({ open, onCancel, onConfirm }: EnrollmentInfoModalProps) {
  const t = useTranslations('Persons.form.face');

  if (!open) return null;

  return createPortal(
    <>
      <div
        onClick={onCancel}
        style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.55)', zIndex: 70 }}
        aria-hidden="true"
      />

      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="face-enroll-info-title"
        style={{
          position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
          width: 'min(440px, calc(100vw - 32px))',
          background: 'var(--sf-raised)',
          borderRadius: '16px',
          boxShadow: '0 16px 48px rgba(0, 0, 0, 0.3)',
          padding: '28px',
          zIndex: 71,
          display: 'flex', flexDirection: 'column', gap: '20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <ScanFrameIllustration />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', textAlign: 'center' }}>
          <h2 id="face-enroll-info-title" style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ct-primary)' }}>
            {t('infoTitle')}
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--ct-secondary)', lineHeight: 1.5 }}>
            {t('infoBody')}
          </p>
        </div>

        <ul style={{ display: 'flex', flexDirection: 'column', gap: '8px', listStyle: 'none', padding: 0, margin: 0 }}>
          {TIP_KEYS.map(key => (
            <li
              key={key}
              style={{
                display: 'flex', alignItems: 'flex-start', gap: '8px',
                fontSize: '12.5px', color: 'var(--ct-secondary)',
              }}
            >
              <span style={{ color: 'var(--rc-accent)', fontWeight: 700, lineHeight: '1.4' }}>•</span>
              <span>{t(`tips.${key}`)}</span>
            </li>
          ))}
        </ul>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <Button type="button" variant="secondary" onClick={onCancel}>
            {t('cancelButton')}
          </Button>
          <Button type="button" variant="primary" onClick={onConfirm}>
            {t('startButton')}
          </Button>
        </div>
      </div>
    </>,
    document.body,
  );
}
