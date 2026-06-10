import { ScanSmiley } from '@phosphor-icons/react';

/**
 * Minimalist "viewfinder" illustration: corner brackets framing a face icon,
 * used to set the tone for the facial-recognition tutorial modal.
 */
export function ScanFrameIllustration() {
  const accent = 'var(--rc-accent)';
  const corner = (transform: string) => (
    <path
      d="M0 16 V4 A4 4 0 0 1 4 0 H16"
      stroke={accent}
      strokeWidth="3.5"
      strokeLinecap="round"
      fill="none"
      transform={transform}
    />
  );

  return (
    <div style={{ position: 'relative', width: '108px', height: '108px' }}>
      <svg viewBox="0 0 108 108" width="108" height="108" style={{ position: 'absolute', inset: 0 }}>
        <g transform="translate(2, 2)">{corner('')}</g>
        <g transform="translate(106, 2)">{corner('rotate(90)')}</g>
        <g transform="translate(106, 106)">{corner('rotate(180)')}</g>
        <g transform="translate(2, 106)">{corner('rotate(270)')}</g>
      </svg>

      <div
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <div
          style={{
            width: '64px', height: '64px', borderRadius: '9999px',
            background: 'var(--ac-subtle)', color: accent,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <ScanSmiley size={36} weight="duotone" />
        </div>
      </div>
    </div>
  );
}
