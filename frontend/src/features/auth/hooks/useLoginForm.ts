'use client';

import { useState, type FormEvent } from 'react';
import { ApiError } from '@/lib/api/client';
import { useAuth } from './useAuth';

type LoginErrorKey = 'errorInvalidCredentials' | 'errorGeneric';

interface UseLoginFormResult {
  email: string;
  password: string;
  isSubmitting: boolean;
  errorKey: LoginErrorKey | null;
  setEmail: (value: string) => void;
  setPassword: (value: string) => void;
  handleSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function useLoginForm(): UseLoginFormResult {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorKey, setErrorKey] = useState<LoginErrorKey | null>(null);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorKey(null);
    setIsSubmitting(true);

    login({ email, password })
      .catch((error: unknown) => {
        if (error instanceof ApiError && (error.status === 401 || error.status === 400)) {
          setErrorKey('errorInvalidCredentials');
        } else {
          setErrorKey('errorGeneric');
        }
      })
      .finally(() => setIsSubmitting(false));
  };

  return { email, password, isSubmitting, errorKey, setEmail, setPassword, handleSubmit };
}
