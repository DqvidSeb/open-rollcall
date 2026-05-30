import { redirect } from '@/lib/i18n/navigation';

// /:locale → /:locale/dashboard
// Locale-aware: /es redirects to /es/dashboard, / redirects to /dashboard
export default function LocaleRootPage() {
  redirect('/dashboard');
}
