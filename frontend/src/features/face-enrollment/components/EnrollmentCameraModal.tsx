'use client';

import { createPortal } from 'react-dom';
import { useTranslations } from 'next-intl';
import { CheckCircle, WarningCircle, X } from '@phosphor-icons/react';
import { Button } from '@/components/ui/Button/Button';
import { useCamera } from '../hooks/useCamera';
import { useFaceCapture } from '../hooks/useFaceCapture';
import { CaptureGuideOverlay } from './CaptureGuideOverlay';
import type { FaceEnrollResult } from '../types';

interface EnrollmentCameraModalProps {
  open: boolean;
  personId: string;
  onClose: () => void;
  onEnrolled: (result: FaceEnrollResult) => void;
}

/**
 * Full guided camera capture flow: requests camera access, walks the user
 * through 5 angles with countdowns and quality checks, then uploads.
 */
export function EnrollmentCameraModal({ open, personId, onClose, onEnrolled }: EnrollmentCameraModalProps) {
  const t = useTranslations('Persons.form.face');
  const { videoRef, isReady, error: cameraError } = useCamera(open);
  const { phase, currentStep, countdown, thumbnail, qualityWarning, retry } =
    useFaceCapture({ personId, videoRef, cameraReady: isReady, onEnrolled });

  if (!open) return null;

  const showVideo = !cameraError && (phase === 'positioning' || phase === 'countdown' || phase === 'captured');

  return createPortal(
    <>
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.6)', zIndex: 80 }} aria-hidden="true" />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="face-enroll-camera-title"
        style={{
          position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
          width: 'min(420px, calc(100vw - 24px))',
          background: 'var(--sf-raised)',
          borderRadius: '14px',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.3)',
          zIndex: 81,
          overflow: 'hidden',
          display: 'flex', flexDirection: 'column',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px' }}>
          <h2 id="face-enroll-camera-title" style={{ fontSize: '14.5px', fontWeight: 600, color: 'var(--ct-primary)' }}>
            {t('cameraTitle')}
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('cancelButton')}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              width: '28px', height: '28px', borderRadius: '9999px', border: 'none',
              background: 'transparent', color: 'var(--ct-secondary)', cursor: 'pointer',
            }}
          >
            <X size={16} weight="bold" />
          </button>
        </div>

        <div style={{ position: 'relative', width: '100%', aspectRatio: '4 / 5', background: '#000' }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%', height: '100%', objectFit: 'cover',
              transform: 'scaleX(-1)',
              display: showVideo ? 'block' : 'none',
            }}
          />

          {showVideo && (
            <CaptureGuideOverlay
              phase={phase}
              currentStep={currentStep}
              countdown={countdown}
              qualityWarning={qualityWarning}
            />
          )}

          {phase === 'captured' && thumbnail && (
            <div
              style={{
                position: 'absolute', inset: 0, background: 'rgba(0, 0, 0, 0.55)',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '10px',
              }}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={thumbnail} alt="" style={{ width: '120px', height: '120px', objectFit: 'cover', borderRadius: '12px', border: '2px solid #fff' }} />
              <CheckCircle size={28} weight="fill" color="#22c55e" />
              <span style={{ color: '#fff', fontSize: '13px' }}>{t('capturedLabel')}</span>
            </div>
          )}

          {(phase === 'requesting-camera' || phase === 'uploading') && !cameraError && (
            <StatusPanel spinning label={phase === 'uploading' ? t('uploadingLabel') : t('requestingCameraLabel')} />
          )}

          {(cameraError || phase === 'error') && (
            <StatusPanel
              icon={<WarningCircle size={28} weight="fill" color="#f59e0b" />}
              label={cameraError ? t('cameraErrorLabel') : t('uploadErrorLabel')}
            />
          )}

          {phase === 'success' && (
            <StatusPanel icon={<CheckCircle size={28} weight="fill" color="#22c55e" />} label={t('successLabel')} />
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', padding: '14px 16px' }}>
          {phase === 'error' && !cameraError && (
            <Button type="button" variant="primary" onClick={retry}>
              {t('retryButton')}
            </Button>
          )}
          {phase === 'success' ? (
            <Button type="button" variant="primary" onClick={onClose}>
              {t('doneButton')}
            </Button>
          ) : (
            <Button type="button" variant="secondary" onClick={onClose}>
              {t('cancelButton')}
            </Button>
          )}
        </div>
      </div>
    </>,
    document.body,
  );
}

function StatusPanel({ spinning, icon, label }: { spinning?: boolean; icon?: React.ReactNode; label: string }) {
  return (
    <div
      style={{
        position: 'absolute', inset: 0, background: 'rgba(0, 0, 0, 0.55)', color: '#fff',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '10px',
        textAlign: 'center', padding: '0 24px',
      }}
    >
      {spinning && <span className="h-7 w-7 border-2 border-current border-t-transparent rounded-full animate-spin" />}
      {icon}
      <span style={{ fontSize: '13px' }}>{label}</span>
    </div>
  );
}
