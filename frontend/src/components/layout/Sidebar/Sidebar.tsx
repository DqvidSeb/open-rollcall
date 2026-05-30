'use client';

import { SquaresFour, UsersThree, TreeStructure, Medal } from '@phosphor-icons/react';
import { useTranslations } from 'next-intl';
import type { Icon } from '@phosphor-icons/react';
import { Logo } from '@/components/ui/Logo';
import { SidebarNavLink } from './SidebarNavLink';
import { SidebarBottom } from './SidebarBottom';

interface NavItem {
  href:     string;
  labelKey: string;
  icon:     Icon;
}

const NAV_ITEMS: NavItem[] = [
  { href: '/dashboard',  labelKey: 'home',        icon: SquaresFour   },
  { href: '/students',   labelKey: 'people',      icon: UsersThree    },
  { href: '/departments', labelKey: 'departments', icon: TreeStructure },
  { href: '/positions',  labelKey: 'positions',   icon: Medal         },
];

export function Sidebar() {
  const t = useTranslations('Nav');

  return (
    <aside
      className="w-[232px] h-screen flex flex-col flex-shrink-0"
      style={{ background: 'var(--sb-bg)' }}
      /* border-right intentionally removed — sidebar merges visually with header */
    >
      {/* ── Brand — bottom padding creates the breathing room to first nav item ── */}
      <div className="px-5 pt-6 pb-6">
        <Logo size={26} showText />
      </div>
      {/* No divider line — spacing alone separates logo from nav */}

      {/* ── Main nav ──────────────────────────────────────────────────────────── */}
      <nav
        className="flex-1 overflow-y-auto px-3 flex flex-col gap-1"
        aria-label={t('mainNav')}
      >
        {NAV_ITEMS.map(({ href, labelKey, icon }) => (
          <SidebarNavLink
            key={href}
            href={href}
            label={t(labelKey)}
            icon={icon}
          />
        ))}
      </nav>

      {/* ── Bottom ────────────────────────────────────────────────────────────── */}
      <SidebarBottom />
    </aside>
  );
}
