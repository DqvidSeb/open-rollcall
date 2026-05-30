import { useTranslations } from 'next-intl';
import Link from 'next/link';

export default function NotFound() {
  const t = useTranslations('Errors');

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-6xl font-bold text-gray-800">404</h1>
      <p className="text-xl text-gray-500">{t('pageNotFound')}</p>
      <Link href="/dashboard" className="text-primary-600 underline">
        {t('goHome')}
      </Link>
    </div>
  );
}
