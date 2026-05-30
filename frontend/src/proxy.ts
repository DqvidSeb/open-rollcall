import createMiddleware from 'next-intl/middleware';
import { routing } from '@/lib/i18n/routing';

// Next.js 16+: proxy.ts replaces middleware.ts for request interception.
// next-intl uses this to handle locale detection and routing.
export default createMiddleware(routing);

export const config = {
  // Match all pathnames except API routes, Next.js internals, and static assets
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|icons|images).*)'],
};
