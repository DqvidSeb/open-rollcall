import { redirect } from '@/lib/i18n/navigation';

// /:locale (via route group) → redirect to the canonical /dashboard URL
export default function DashboardGroupRoot() {
  redirect('/dashboard');
}
