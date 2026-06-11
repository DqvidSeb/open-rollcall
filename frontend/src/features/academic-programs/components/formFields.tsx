'use client';

export const textareaClassName =
  'w-full rounded-lg border bg-surface-raised text-content-primary px-3 py-2 text-sm ' +
  'placeholder:text-[var(--input-placeholder)] resize-none ' +
  'transition-colors duration-150 focus:outline-none focus:border-[var(--input-focus-border)] ' +
  'border-[var(--input-border)] disabled:opacity-60 disabled:cursor-not-allowed';

interface FieldProps {
  label: string;
  hint?: string;
  children: React.ReactNode;
}

export function Field({ label, hint, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-content-secondary">{label}</label>
      {children}
      {hint && <p className="text-xs text-content-secondary">{hint}</p>}
    </div>
  );
}
