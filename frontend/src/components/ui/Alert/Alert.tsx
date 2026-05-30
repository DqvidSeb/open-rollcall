import { clsx } from 'clsx';

export type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  message: string;
  onClose?: () => void;
}

const variantConfig: Record<AlertVariant, { container: string; title: string }> = {
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    title: 'text-blue-900',
  },
  success: {
    container: 'bg-green-50 border-green-200 text-green-800',
    title: 'text-green-900',
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    title: 'text-yellow-900',
  },
  error: {
    container: 'bg-red-50 border-red-200 text-red-800',
    title: 'text-red-900',
  },
};

export function Alert({ variant = 'info', title, message, onClose }: AlertProps) {
  const config = variantConfig[variant];

  return (
    <div
      role="alert"
      className={clsx('flex gap-3 rounded-lg border p-4', config.container)}
    >
      <div className="flex-1">
        {title && (
          <p className={clsx('text-sm font-semibold mb-1', config.title)}>{title}</p>
        )}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          aria-label="Dismiss"
          className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
        >
          ✕
        </button>
      )}
    </div>
  );
}
