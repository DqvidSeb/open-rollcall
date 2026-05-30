import { clsx } from 'clsx';

export type SpinnerSize = 'sm' | 'md' | 'lg';

interface SpinnerProps {
  size?: SpinnerSize;
  className?: string;
  label?: string;
}

const sizeClasses: Record<SpinnerSize, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-4',
};

export function Spinner({ size = 'md', className, label = 'Loading...' }: SpinnerProps) {
  return (
    <div role="status" className="inline-flex items-center justify-center">
      <span
        className={clsx(
          'rounded-full border-primary-600 border-t-transparent animate-spin',
          sizeClasses[size],
          className,
        )}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}
