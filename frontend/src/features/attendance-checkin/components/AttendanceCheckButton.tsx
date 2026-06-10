'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { ScanSmiley } from '@phosphor-icons/react';
import { AttendanceInfoModal } from './AttendanceInfoModal';
import { AttendanceCameraModal } from './AttendanceCameraModal';

/**
 * Sidebar action button that launches the check-in/check-out flow:
 * an info/tutorial modal followed by the live recognition camera.
 */
export function AttendanceCheckButton() {
  const t = useTranslations('Attendance.checkin');
  const [showInfo, setShowInfo]     = useState(false);
  const [showCamera, setShowCamera] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setShowInfo(true)}
        style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
          width: '100%',
          padding: '8px 18px',
          borderRadius: '9999px',
          border: 'none',
          background: '#f97316',
          color: '#fff',
          fontSize: '13.5px',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'background 130ms ease',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = '#ea580c'; }}
        onMouseLeave={e => { e.currentTarget.style.background = '#f97316'; }}
      >
        <ScanSmiley size={26} weight="fill" color="#fff" />
        {t('sidebarButton')}
      </button>

      <AttendanceInfoModal
        open={showInfo}
        onCancel={() => setShowInfo(false)}
        onConfirm={() => { setShowInfo(false); setShowCamera(true); }}
      />

      <AttendanceCameraModal
        open={showCamera}
        onClose={() => setShowCamera(false)}
      />
    </>
  );
}
