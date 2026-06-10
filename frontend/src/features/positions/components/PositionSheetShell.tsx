'use client';

interface PositionSheetShellProps {
  open: boolean;
  onClose: () => void;
  labelledBy: string;
  children: React.ReactNode;
}

/** Shared right-side sliding sheet shell (overlay + panel) for position sheets. */
export function PositionSheetShell({ open, onClose, labelledBy, children }: PositionSheetShellProps) {
  return (
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
        style={{
          position:   'fixed',
          inset:      0,
          background: 'rgba(0, 0, 0, 0.45)',
          opacity:    open ? 1 : 0,
          pointerEvents: open ? 'auto' : 'none',
          transition: 'opacity 200ms ease',
          zIndex:     50,
        }}
        aria-hidden="true"
      />

      {/* Sheet */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        style={{
          position:   'fixed',
          top:        0,
          right:      0,
          bottom:     0,
          width:      'min(440px, 100vw)',
          background: 'var(--page-bg)',
          borderLeft: '1px solid var(--sf-border)',
          boxShadow:  '-8px 0 32px rgba(0, 0, 0, 0.18)',
          transform:  open ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 240ms ease',
          zIndex:     51,
          display:    'flex',
          flexDirection: 'column',
        }}
      >
        {children}
      </div>
    </>
  );
}
