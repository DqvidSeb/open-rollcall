'use client';

import { SquaresFour, UsersThree, TreeStructure, Medal, GraduationCap } from '@phosphor-icons/react';
import { useTranslations } from 'next-intl';
import type { Icon } from '@phosphor-icons/react';
import { Logo } from '@/components/ui/Logo';
import { AttendanceCheckButton } from '@/features/attendance-checkin/components/AttendanceCheckButton';
import { SidebarNavLink } from './SidebarNavLink';
import { SidebarBottom } from './SidebarBottom';

interface NavItem {
  href:     string;
  labelKey: string;
  icon:     Icon;
}

interface NavSection {
  titleKey: string;
  items:    NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    titleKey: 'sectionMain',
    items: [
      { href: '/dashboard', labelKey: 'home',   icon: SquaresFour },
      { href: '/persons',   labelKey: 'people', icon: UsersThree  },
    ],
  },
  {
    titleKey: 'sectionStudents',
    items: [
      { href: '/academic-programs', labelKey: 'academicPrograms', icon: GraduationCap },
    ],
  },
  {
    titleKey: 'sectionEmployees',
    items: [
      { href: '/departments', labelKey: 'departments', icon: TreeStructure },
      { href: '/positions',   labelKey: 'positions',   icon: Medal         },
    ],
  },
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
        className="flex-1 overflow-y-auto px-3 flex flex-col"
        aria-label={t('mainNav')}
      >
        <div className="px-1 pb-4">
          <AttendanceCheckButton />
        </div>

        {NAV_SECTIONS.map(({ titleKey, items }) => (
          <div key={titleKey} className="flex flex-col gap-1 pb-4">
            <span
              className="px-3 pb-1 font-semibold uppercase"
              style={{ color: 'var(--sb-section-label)', fontSize: '10.5px', letterSpacing: '0.04em' }}
            >
              {t(titleKey)}
            </span>
            {items.map(({ href, labelKey, icon }) => (
              <SidebarNavLink
                key={href}
                href={href}
                label={t(labelKey)}
                icon={icon}
              />
            ))}
          </div>
        ))}
      </nav>

      {/* ── Bottom ────────────────────────────────────────────────────────────── */}
      <SidebarBottom />
    </aside>
  );
}
