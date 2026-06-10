'use client';

import { GearSix, SealQuestion } from '@phosphor-icons/react';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { SidebarNavLink } from './SidebarNavLink';
import { ThemeToggle } from './ThemeToggle';
import { UserButton } from './UserButton';

export function SidebarBottom() {
  const t = useTranslations('Nav');
  const { user, logout } = useAuth();

  return (
    <div className="flex flex-col gap-1 px-3 pb-4">

      {/* ── Divider ───────────────────────────────────── */}
      <div style={{ height: 1, background: 'var(--sb-divider)', margin: '0 4px 8px' }} />

      <SidebarNavLink href="/settings" label={t('settings')}   icon={GearSix}      />
      <SidebarNavLink href="/help"     label={t('helpCenter')} icon={SealQuestion} />
      <ThemeToggle />

      {/* ── User profile ──────────────────────────────── */}
      <UserButton
        name={user?.fullName ?? ''}
        email={user?.email ?? undefined}
        logoutLabel={t('logout')}
        onLogout={logout}
      />

    </div>
  );
}
