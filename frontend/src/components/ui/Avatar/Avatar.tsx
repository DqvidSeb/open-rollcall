import Image from 'next/image';
import { clsx } from 'clsx';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface AvatarProps {
  src?: string | null;
  alt: string;
  size?: AvatarSize;
  className?: string;
}

const sizeClasses: Record<AvatarSize, string> = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
  xl: 'h-16 w-16 text-lg',
};

const pixelSizes: Record<AvatarSize, number> = {
  xs: 24,
  sm: 32,
  md: 40,
  lg: 48,
  xl: 64,
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

export function Avatar({ src, alt, size = 'md', className }: AvatarProps) {
  const px = pixelSizes[size];

  if (src) {
    return (
      <div className={clsx('relative rounded-full overflow-hidden flex-shrink-0', sizeClasses[size], className)}>
        <Image src={src} alt={alt} width={px} height={px} className="object-cover" />
      </div>
    );
  }

  return (
    <div
      className={clsx(
        'rounded-full bg-primary-100 text-primary-700 font-semibold',
        'flex items-center justify-center flex-shrink-0',
        sizeClasses[size],
        className,
      )}
      aria-label={alt}
    >
      {getInitials(alt)}
    </div>
  );
}
