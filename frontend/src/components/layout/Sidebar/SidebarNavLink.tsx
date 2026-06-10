'use client';

import { useState } from 'react';
import { Link, usePathname } from '@/lib/i18n/navigation';
import type { Icon, IconWeight } from '@phosphor-icons/react';

interface SidebarNavLinkProps {
  href:  string;
  label: string;
  icon:  Icon;
}

/**
 * Sidebar navigation link — three visual states:
 *
 * ACTIVE  → pill bg (--sb-active-bg)  + accent text (--sb-active-text)  + duotone icon
 * HOVER   → soft bg (--sb-hover-bg)   + secondary text (--sb-hover-text) + duotone icon
 * IDLE    → transparent               + muted text (--sb-muted)           + regular icon
 *
 * Light mode: active = gray pill + orange text/icon
 * Dark  mode: active = neutral gray pill + orange text/icon
 *
 * All colours are CSS custom-property–backed → zero hardcoded values in JS.
 */
export function SidebarNavLink({ href, label, icon: IconComponent }: SidebarNavLinkProps) {
  const pathname  = usePathname();
  const [hovered, setHovered] = useState(false);

  const isActive = pathname === href || pathname.startsWith(`${href}/`);

  // Icon weight: duotone when active OR hovered, regular when idle
  const iconWeight: IconWeight = (isActive || hovered) ? 'duotone' : 'regular';

  // Inline style driven entirely by CSS vars — adapts to light/dark automatically
  const style: React.CSSProperties = isActive
    ? {
        background: 'var(--sb-active-bg)',
        color:      'var(--sb-active-text)',
        fontWeight: 600,
        boxShadow:  'var(--sb-active-shadow)',
      }
    : hovered
    ? {
        background: 'var(--sb-hover-bg)',
        color:      'var(--sb-hover-text)',
        fontWeight: 500,
      }
    : {
        background: 'transparent',
        color:      'var(--sb-muted)',
        fontWeight: 500,
      };

  return (
    <Link
      href={href}
      aria-current={isActive ? 'page' : undefined}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display:        'flex',
        alignItems:     'center',
        gap:            '10px',
        padding:        '8px 11px',
        borderRadius:   '8px',
        fontSize:       '13.5px',
        letterSpacing:  '-0.01em',
        textDecoration: 'none',
        userSelect:     'none',
        transition:     'background 130ms ease, color 130ms ease, box-shadow 130ms ease',
        ...style,
      }}
    >
      <IconComponent
        size={17}
        weight={iconWeight}
        aria-hidden="true"
        style={{ flexShrink: 0 }}
      />
      {label}
    </Link>
  );
}
