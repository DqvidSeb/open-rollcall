import { type InputHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, leftAddon, rightAddon, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-content-secondary">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftAddon && (
            <span className="absolute left-3 text-content-disabled">{leftAddon}</span>
          )}
          <input
            id={inputId}
            ref={ref}
            className={clsx(
              'w-full rounded-lg border bg-surface-raised text-content-primary px-3 py-2 text-sm',
              'placeholder:text-[var(--input-placeholder)]',
              'transition-colors duration-150',
              'focus:outline-none focus:border-[var(--input-focus-border)]',
              'disabled:opacity-60 disabled:cursor-not-allowed',
              error ? 'border-red-500' : 'border-[var(--input-border)]',
              leftAddon && 'pl-9',
              rightAddon && 'pr-9',
              className,
            )}
            {...props}
          />
          {rightAddon && (
            <span className="absolute right-3 text-content-disabled">{rightAddon}</span>
          )}
        </div>
        {error && <p className="text-xs text-red-600">{error}</p>}
        {hint && !error && <p className="text-xs text-content-secondary">{hint}</p>}
      </div>
    );
  },
);

Input.displayName = 'Input';
