'use client';

import { createPortal } from 'react-dom';
import { useTranslations } from 'next-intl';
import { WarningCircle, X } from '@phosphor-icons/react';
import { Button } from '@/components/ui/Button/Button';
import { useCamera } from '@/features/face-enrollment/hooks/useCamera';
import { useAttendanceRecognition } from '../hooks/useAttendanceRecognition';
import { AttendanceResultPanel } from './AttendanceResultPanel';

interface AttendanceCameraModalProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Wide (landscape) live camera feed for the check-in/check-out flow.
 * Mirrors the backend's `camera_client.py attend` script: continuously
 * scans for a face, shows a confirmation overlay on a successful match,
 * and surfaces out-of-window or connection issues.
 */
export function AttendanceCameraModal({ open, onClose }: AttendanceCameraModalProps) {
  const t = useTranslations('Attendance.checkin');
  const { videoRef, isReady, error: cameraError } = useCamera(open);
  const { phase, result, message, retry } = useAttendanceRecognition({ videoRef, cameraReady: isReady });

  if (!open) return null;

  const showVideo = !cameraError && phase !== 'error';

  return createPortal(
    <>
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.6)', zIndex: 80 }} aria-hidden="true" />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="attendance-camera-title"
        style={{
          position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
          width: 'min(820px, calc(100vw - 24px))',
          background: 'var(--sf-raised)',
          borderRadius: '14px',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.3)',
          zIndex: 81,
          overflow: 'hidden',
          display: 'flex', flexDirection: 'column',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px' }}>
          <h2 id="attendance-camera-title" style={{ fontSize: '14.5px', fontWeight: 600, color: 'var(--ct-primary)' }}>
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

        <div style={{ position: 'relative', width: '100%', aspectRatio: '16 / 9', background: '#000' }}>
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

          {showVideo && <AttendanceResultPanel phase={phase} result={result} message={message} />}

          {phase === 'requesting-camera' && !cameraError && (
            <StatusPanel spinning label={t('requestingCameraLabel')} />
          )}

          {cameraError && (
            <StatusPanel
              icon={<WarningCircle size={28} weight="fill" color="#f59e0b" />}
              label={t('cameraErrorLabel')}
            />
          )}

          {phase === 'blocked' && (
            <StatusPanel
              icon={<WarningCircle size={28} weight="fill" color="#fbbf24" />}
              label={message ?? t('blockedLabel')}
            />
          )}

          {phase === 'error' && !cameraError && (
            <StatusPanel
              icon={<WarningCircle size={28} weight="fill" color="#f59e0b" />}
              label={message ?? t('connectionErrorLabel')}
            />
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', padding: '14px 16px' }}>
          {phase === 'error' && !cameraError && (
            <Button type="button" variant="primary" onClick={retry}>
              {t('retryButton')}
            </Button>
          )}
          <Button type="button" variant="secondary" onClick={onClose}>
            {t('doneButton')}
          </Button>
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
