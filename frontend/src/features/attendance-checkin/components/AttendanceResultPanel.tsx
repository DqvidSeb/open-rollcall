'use client';

import { useTranslations } from 'next-intl';
import { CheckCircle, Scan, WarningCircle } from '@phosphor-icons/react';
import type { AttendanceCheckResult, RecognitionPhase } from '../types';

interface AttendanceResultPanelProps {
  phase:   RecognitionPhase;
  result:  AttendanceCheckResult | null;
  message: string | null;
}

/**
 * Live feedback overlay shown on top of the camera preview, mirroring the
 * backend's `attend` script: a "scanning" badge, a big confirmation check
 * with the recognized person's name and event type, or a brief hint when a
 * face isn't recognized.
 */
export function AttendanceResultPanel({ phase, result, message }: AttendanceResultPanelProps) {
  const t = useTranslations('Attendance.checkin');

  if (phase === 'scanning') {
    return (
      <Badge icon={<Scan size={16} weight="bold" />} label={t('scanningLabel')} color="#fff" />
    );
  }

  if (phase === 'no-match') {
    return (
      <Badge
        icon={<WarningCircle size={16} weight="fill" />}
        label={message ?? t('noMatchLabel')}
        color="#fbbf24"
      />
    );
  }

  if (phase === 'recognized' && result) {
    const isCheckIn = result.event_type === 'check_in';
    const color = isCheckIn ? '#22c55e' : '#facc15';
    const eventLabel = isCheckIn ? t('checkInRegistered') : t('checkOutRegistered');
    const subLabel = isCheckIn ? t('welcomeMessage') : t('seeYouMessage');
    const time = new Date(result.event_time).toLocaleTimeString();

    return (
      <div
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          gap: '12px', background: 'rgba(0, 0, 0, 0.45)',
        }}
      >
        <span style={{ fontSize: '13px', fontWeight: 700, color, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          {eventLabel}
        </span>
        <CheckCircle size={64} weight="fill" color={color} />
        <span style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>{subLabel}</span>

        <div
          style={{
            marginTop: '8px', width: 'calc(100% - 32px)', maxWidth: '420px',
            background: 'rgba(18, 18, 18, 0.85)', borderRadius: '10px',
            borderTop: `3px solid ${color}`, padding: '12px 16px',
            display: 'flex', flexDirection: 'column', gap: '4px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>{result.full_name ?? '—'}</span>
            <span style={{ fontSize: '13px', fontWeight: 700, color }}>{time}</span>
          </div>
          {result.employee_code && (
            <span style={{ fontSize: '12px', color: '#a3a3a3' }}>{t('codeLabel')}: {result.employee_code}</span>
          )}
        </div>
      </div>
    );
  }

  return null;
}

function Badge({ icon, label, color }: { icon: React.ReactNode; label: string; color: string }) {
  return (
    <div
      style={{
        position: 'absolute', top: '14px', left: '14px',
        display: 'inline-flex', alignItems: 'center', gap: '8px',
        background: 'rgba(0, 0, 0, 0.55)', borderRadius: '9999px',
        padding: '6px 14px', color, fontSize: '12.5px', fontWeight: 600,
      }}
    >
      {icon}
      <span>{label}</span>
    </div>
  );
}
