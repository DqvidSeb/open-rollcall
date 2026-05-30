'use client';

import { useState } from 'react';
import { Moon, Sun } from '@phosphor-icons/react';
import { useTranslations } from 'next-intl';
import { useTheme } from '@/lib/theme/ThemeProvider';

/**
 * Dark-mode toggle.
 * Follows the same three-state visual logic as SidebarNavLink:
 *   IDLE  → muted text + regular icon
 *   HOVER → secondary text + duotone icon + soft bg
 * (Never "active" in the nav sense — it's always idle or hovered.)
 *
 * Toggle pill math (40 × 22 px container, 16 × 16 px knob, 3 px padding):
 *   OFF → translateX(0)    knob at left  [3 → 19 px]
 *   ON  → translateX(18px) knob at right [21 → 37 px, 3 px gap ✓]
 */
export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const t = useTranslations('Nav');
  const [hovered, setHovered] = useState(false);
  const isDark = theme === 'dark';

  const style: React.CSSProperties = hovered
    ? { background: 'var(--sb-hover-bg)', color: 'var(--sb-hover-text)' }
    : { background: 'transparent',        color: 'var(--sb-muted)'      };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display:       'flex',
        alignItems:    'center',
        gap:           '10px',
        padding:       '8px 11px',
        borderRadius:  '8px',
        fontSize:      '13.5px',
        fontWeight:    500,
        letterSpacing: '-0.01em',
        border:        'none',
        cursor:        'pointer',
        width:         '100%',
        userSelect:    'none',
        transition:    'background 130ms ease, color 130ms ease',
        ...style,
      }}
    >
      {/* Icon: duotone on hover, regular when idle */}
      {isDark
        ? <Sun  size={17} weight={hovered ? 'duotone' : 'regular'} aria-hidden="true" style={{ flexShrink: 0 }} />
        : <Moon size={17} weight={hovered ? 'duotone' : 'regular'} aria-hidden="true" style={{ flexShrink: 0 }} />
      }

      <span style={{ flex: 1, textAlign: 'left' }}>
        {isDark ? t('lightTheme') : t('darkTheme')}
      </span>

      {/* Toggle pill */}
      <div
        aria-hidden="true"
        style={{
          position:     'relative',
          flexShrink:   0,
          width:        '40px',
          height:       '22px',
          borderRadius: '999px',
          background:   isDark ? 'var(--rc-accent)' : 'var(--rc-gray)',
          transition:   'background 200ms ease',
        }}
      >
        <span
          style={{
            position:     'absolute',
            top:          '3px',
            left:         '3px',
            width:        '16px',
            height:       '16px',
            borderRadius: '50%',
            background:   '#FFFFFF',
            boxShadow:    '0 1px 3px rgba(0,0,0,0.18)',
            transition:   'transform 200ms ease',
            transform:    isDark ? 'translateX(18px)' : 'translateX(0)',
          }}
        />
      </div>
    </button>
  );
}
