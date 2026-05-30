import { getTranslations } from 'next-intl/server';
import { LoginForm } from '@/features/auth/components/LoginForm';

export async function generateMetadata() {
  const t = await getTranslations('Auth');
  return { title: t('loginTitle') };
}

export default function LoginPage() {
  return <LoginForm />;
}
