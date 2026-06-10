'use client';

import { useTranslations } from 'next-intl';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { Logo } from '@/components/ui/Logo';
import { useLoginForm } from '../hooks/useLoginForm';

export function LoginForm() {
  const t = useTranslations('Auth');
  const { email, password, isSubmitting, errorKey, setEmail, setPassword, handleSubmit } =
    useLoginForm();

  return (
    <div className="w-full max-w-sm flex flex-col items-center gap-6">
      <Logo size={32} showText />

      <div
        className="w-full flex flex-col gap-6 p-8"
        style={{
          background: 'var(--sf-raised)',
          border: '1px solid var(--sf-border)',
          borderRadius: '8px',
        }}
      >
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--ct-primary)' }}>
            {t('loginTitle')}
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--ct-secondary)' }}>
            {t('loginSubtitle')}
          </p>
        </div>

        {errorKey && <Alert variant="error" message={t(errorKey)} />}

        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <Input
            label={t('emailLabel')}
            type="email"
            placeholder={t('emailPlaceholder')}
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <Input
            label={t('passwordLabel')}
            type="password"
            placeholder={t('passwordPlaceholder')}
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <Button type="submit" className="w-full justify-center" isLoading={isSubmitting}>
            {isSubmitting ? t('loggingIn') : t('loginButton')}
          </Button>
        </form>
      </div>
    </div>
  );
}
