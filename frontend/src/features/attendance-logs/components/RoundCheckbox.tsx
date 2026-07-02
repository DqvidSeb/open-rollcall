'use client';

interface RoundCheckboxProps {
  checked:   boolean;
  onChange:  (checked: boolean) => void;
  ariaLabel?: string;
}

/**
 * Branded checkbox with rounded corners.
 * Unchecked : border --tbl-check-border, transparent fill.
 * Checked   : fill --rc-accent, white checkmark, no border.
 * Focus     : accent outline ring.
 */
export function RoundCheckbox({ checked, onChange, ariaLabel }: RoundCheckboxProps) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={checked}
      aria-label={ariaLabel}
      onClick={e => { e.stopPropagation(); onChange(!checked); }}
      style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'center',
        width:          '17px',
        height:         '17px',
        borderRadius:   '5px',
        border:         checked ? 'none' : '1.5px solid var(--tbl-check-border)',
        background:     checked ? 'var(--rc-accent)' : 'transparent',
        cursor:         'pointer',
        flexShrink:     0,
        transition:     'background 120ms ease, border 120ms ease',
        outline:        'none',
      }}
      onFocus={e  => { e.currentTarget.style.boxShadow = '0 0 0 2px var(--rc-accent-12)'; }}
      onBlur={e   => { e.currentTarget.style.boxShadow = 'none'; }}
    >
      {checked && (
        <svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true">
          <path
            d="M1 4L3.8 7L9 1"
            stroke="var(--rc-ink)"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
  );
}
