import { getTranslations } from 'next-intl/server';
import { RegisterForm } from '@/features/auth/components/RegisterForm';

export async function generateMetadata() {
  const t = await getTranslations('Auth');
  return { title: t('registerTitle') };
}

export default function RegisterPage() {
  return <RegisterForm />;
}
