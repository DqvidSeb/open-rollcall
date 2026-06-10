'use client';

import { useState } from 'react';
import { SignOut } from '@phosphor-icons/react';

interface UserButtonProps {
  /** Full name — e.g. "David Grijalba" */
  name: string;
  /** Optional subtitle (email, role, etc.) — not shown for now */
  email?: string;
  /** Accessible label for the logout action */
  logoutLabel: string;
  /** Called when the user clicks the logout icon */
  onLogout: () => void;
}

/**
 * User profile button — sits at the very bottom of the sidebar.
 *
 * Avatar  : circle with the first letter of the first name and the first
 *           letter of the last name (e.g. "DG"), accent background.
 * Label   : full "FirstName LastName".
 * Hover   : same orange-tint style as the original header user button.
 * Width   : full sidebar width, matching nav links exactly.
 */
export function UserButton({ name, logoutLabel, onLogout }: UserButtonProps) {
  const [hovered, setHovered] = useState(false);

  // Build initials: first char of word[0] + first char of last word
  const words    = name.trim().split(/\s+/).filter(Boolean);
  const initials = [words[0]?.[0], words[words.length - 1]?.[0]]
    .filter(Boolean)
    .join('')
    .toUpperCase();

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display:       'flex',
        alignItems:    'center',
        gap:           '10px',
        width:         '100%',
        padding:       '8px 11px',
        borderRadius:  '8px',
        userSelect:    'none',
        letterSpacing: '-0.01em',
        fontSize:      '13.5px',
        fontWeight:    500,
        transition:    'background 130ms ease, color 130ms ease',
        background:    hovered ? 'var(--ac-subtle)'  : 'var(--sb-user-bg)',
        color:         hovered ? 'var(--rc-accent)'  : 'var(--sb-text)',
      }}
    >
      {/* ── Avatar circle ─────────────────────────────── */}
      <span
        aria-hidden="true"
        style={{
          flexShrink:     0,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          width:          '26px',
          height:         '26px',
          borderRadius:   '50%',
          background:     'var(--rc-accent)',
          color:          'var(--rc-ink)',
          fontSize:       '10px',
          fontWeight:     700,
          letterSpacing:  '0.02em',
        }}
      >
        {initials}
      </span>

      {/* ── Name ──────────────────────────────────────── */}
      <span style={{ flex: 1, textAlign: 'left', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {name}
      </span>

      {/* ── Logout ────────────────────────────────────── */}
      <button
        type="button"
        onClick={onLogout}
        aria-label={logoutLabel}
        title={logoutLabel}
        style={{
          flexShrink:     0,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          width:          '22px',
          height:         '22px',
          padding:        0,
          border:         'none',
          borderRadius:   '6px',
          background:     'transparent',
          color:          'inherit',
          cursor:         'pointer',
          opacity:        hovered ? 1 : 0,
          transition:     'opacity 130ms ease',
        }}
      >
        <SignOut size={16} aria-hidden="true" />
      </button>
    </div>
  );
}
