'use client';

import { useTranslations } from 'next-intl';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

// LoginForm — stub, to be implemented
// Will use react-hook-form + zod validation
export function LoginForm() {
  const t = useTranslations('Auth');

  return (
    <div className="w-full max-w-sm bg-white rounded-xl shadow-md p-8 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('loginTitle')}</h1>
        <p className="text-sm text-gray-500 mt-1">{t('loginSubtitle')}</p>
      </div>
      <form className="flex flex-col gap-4">
        <Input label={t('emailLabel')} type="email" placeholder={t('emailPlaceholder')} />
        <Input label={t('passwordLabel')} type="password" placeholder={t('passwordPlaceholder')} />
        <Button type="submit" className="w-full">
          {t('loginButton')}
        </Button>
      </form>
    </div>
  );
}
