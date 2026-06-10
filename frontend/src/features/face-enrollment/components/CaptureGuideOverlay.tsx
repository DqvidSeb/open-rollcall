'use client';

import { useTranslations } from 'next-intl';
import { CAPTURE_STEP_KEYS, TOTAL_SAMPLES } from '../constants';
import type { CapturePhase } from '../types';
import type { QualityResult } from '../utils/imageQuality';

interface CaptureGuideOverlayProps {
  phase:          CapturePhase;
  currentStep:    number;
  countdown:      number;
  qualityWarning: QualityResult['reasonKey'];
}

/**
 * Visual guide drawn on top of the camera preview: an oval framing guide,
 * a countdown ring, the per-angle instruction, and quality warnings.
 */
export function CaptureGuideOverlay({ phase, currentStep, countdown, qualityWarning }: CaptureGuideOverlayProps) {
  const t = useTranslations('Persons.form.face');
  const stepKey = CAPTURE_STEP_KEYS[currentStep] ?? CAPTURE_STEP_KEYS[0];
  const isCounting = phase === 'positioning' || phase === 'countdown';

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* Oval framing guide */}
      <div
        style={{
          position: 'absolute',
          top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
          width: '62%', aspectRatio: '3 / 4',
          borderRadius: '50%',
          border: `3px solid ${qualityWarning ? '#f59e0b' : 'var(--rc-accent)'}`,
          boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.35)',
          transition: 'border-color 200ms ease',
        }}
      />

      {/* Countdown ring */}
      {isCounting && (
        <div
          style={{
            position: 'absolute', top: '14px', left: '50%', transform: 'translateX(-50%)',
            width: '40px', height: '40px', borderRadius: '9999px',
            background: 'rgba(0, 0, 0, 0.55)', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '17px', fontWeight: 700,
          }}
        >
          {countdown}
        </div>
      )}

      {/* Step progress dots */}
      <div style={{ position: 'absolute', top: '64px', left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: '6px' }}>
        {Array.from({ length: TOTAL_SAMPLES }).map((_, i) => (
          <span
            key={i}
            style={{
              width: '7px', height: '7px', borderRadius: '9999px',
              background: i <= currentStep ? 'var(--rc-accent)' : 'rgba(255, 255, 255, 0.35)',
            }}
          />
        ))}
      </div>

      {/* Bottom instruction panel */}
      <div
        style={{
          position: 'absolute', bottom: '20px', left: '16px', right: '16px',
          background: 'rgba(0, 0, 0, 0.55)', color: '#fff',
          borderRadius: '12px', padding: '12px 16px',
          textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '4px',
        }}
      >
        <span style={{ fontSize: '14px', fontWeight: 600 }}>{t(`steps.${stepKey}`)}</span>
        {qualityWarning && (
          <span style={{ fontSize: '12.5px', color: '#fbbf24' }}>{t(`quality.${qualityWarning}`)}</span>
        )}
      </div>
    </div>
  );
}
