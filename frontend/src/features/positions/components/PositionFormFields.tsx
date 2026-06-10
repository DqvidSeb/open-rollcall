'use client';

import { useTranslations } from 'next-intl';
import { Input } from '@/components/ui/Input/Input';
import { Field, textareaClassName } from './formFields';

interface PositionFormFieldsProps {
  name:        string;
  description: string;
  onChangeName: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onChangeDescription: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  disabled?: boolean;
  error?: string | null;
  autoFocusName?: boolean;
}

/** Shared name + description fields used by the create and details sheets. */
export function PositionFormFields({
  name, description, onChangeName, onChangeDescription, disabled, error, autoFocusName,
}: PositionFormFieldsProps) {
  const t = useTranslations('Positions.form');

  return (
    <>
      <Input
        label={t('nameLabel')}
        value={name}
        onChange={onChangeName}
        disabled={disabled}
        autoFocus={autoFocusName}
        required
      />

      <Field label={t('descriptionLabel')}>
        <textarea
          className={textareaClassName}
          value={description}
          onChange={onChangeDescription}
          disabled={disabled}
          rows={4}
        />
      </Field>

      {error && (
        <p style={{ fontSize: '13px', color: '#dc2626' }}>{error}</p>
      )}
    </>
  );
}
