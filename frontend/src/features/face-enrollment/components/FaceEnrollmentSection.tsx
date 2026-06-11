'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { CheckCircle, ScanSmiley } from '@phosphor-icons/react';
import { useFaceEnrollmentStatus } from '../hooks/useFaceEnrollmentStatus';
import { EnrollmentInfoModal } from './EnrollmentInfoModal';
import { EnrollmentCameraModal } from './EnrollmentCameraModal';
import type { FaceEnrollResult } from '../types';

interface FaceEnrollmentSectionProps {
  /** Person.id — shared primary key with the employee/student specialization. */
  personId: string;
}

/**
 * "Reconocimiento facial" section shown at the bottom of the person
 * details form. Lets an employee or student register their biometric face data.
 */
export function FaceEnrollmentSection({ personId }: FaceEnrollmentSectionProps) {
  const t = useTranslations('Persons.form.face');

  const { status, isLoading, refetch } = useFaceEnrollmentStatus(personId);
  const [showInfo, setShowInfo]     = useState(false);
  const [showCamera, setShowCamera] = useState(false);

  const handleEnrolled = (_result: FaceEnrollResult) => {
    refetch();
  };

  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingTop: '8px', borderTop: '1px solid var(--sf-border)' }}>
      <h3 style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--ct-primary)' }}>
        {t('sectionTitle')}
      </h3>

      {isLoading && (
        <p style={{ fontSize: '12.5px', color: 'var(--ct-secondary)' }}>{t('statusLoading')}</p>
      )}

      {!isLoading && status?.enrolled && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={18} weight="fill" color="#22c55e" />
          <span style={{ fontSize: '12.5px', color: 'var(--ct-secondary)' }}>
            {t('statusEnrolled', { count: status.samples })}
          </span>
        </div>
      )}

      {!isLoading && status && !status.enrolled && (
        <button
          type="button"
          onClick={() => setShowInfo(true)}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '10px',
            alignSelf: 'flex-start',
            padding: '12px 22px',
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
          {t('registerButton')}
        </button>
      )}

      <EnrollmentInfoModal
        open={showInfo}
        onCancel={() => setShowInfo(false)}
        onConfirm={() => { setShowInfo(false); setShowCamera(true); }}
      />

      <EnrollmentCameraModal
        open={showCamera}
        personId={personId}
        onClose={() => setShowCamera(false)}
        onEnrolled={handleEnrolled}
      />
    </section>
  );
}
