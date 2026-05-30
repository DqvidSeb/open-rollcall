'use client';

import { useTranslations } from 'next-intl';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

// RegisterForm — stub, to be implemented
export function RegisterForm() {
  const t = useTranslations('Auth');

  return (
    <div className="w-full max-w-sm bg-white rounded-xl shadow-md p-8 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('registerTitle')}</h1>
      </div>
      <form className="flex flex-col gap-4">
        <Input label={t('nameLabel')} type="text" placeholder={t('namePlaceholder')} />
        <Input label={t('emailLabel')} type="email" placeholder={t('emailPlaceholder')} />
        <Input label={t('passwordLabel')} type="password" placeholder={t('passwordPlaceholder')} />
        <Input label={t('confirmPasswordLabel')} type="password" placeholder={t('confirmPasswordPlaceholder')} />
        <Button type="submit" className="w-full">
          {t('registerButton')}
        </Button>
      </form>
    </div>
  );
}
