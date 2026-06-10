import createMiddleware from 'next-intl/middleware';
import { NextResponse, type NextRequest } from 'next/server';
import { routing } from '@/lib/i18n/routing';
import { ACCESS_TOKEN_COOKIE } from '@/lib/auth/session';

// Next.js 16+: proxy.ts replaces middleware.ts for request interception.
// next-intl uses this to handle locale detection and routing. We layer a
// lightweight auth guard on top: presence of the access-token cookie gates
// access to the dashboard, and signed-in users are kept out of /login.

const intlMiddleware = createMiddleware(routing);

const PUBLIC_PATHS = ['/login', '/register'];

/** Splits a locale prefix (if any) from the pathname. Returns `[locale, rest]`. */
function splitLocale(pathname: string): [string | null, string] {
  const [, first, ...rest] = pathname.split('/');
  if ((routing.locales as readonly string[]).includes(first)) {
    return [first, `/${rest.join('/')}` || '/'];
  }
  return [null, pathname];
}

function buildPath(locale: string | null, target: string): string {
  return locale ? `/${locale}${target}` : target;
}

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const [locale, path] = splitLocale(pathname);
  const isAuthenticated = request.cookies.has(ACCESS_TOKEN_COOKIE);
  const isPublicPath = PUBLIC_PATHS.some((p) => path === p || path.startsWith(`${p}/`));

  if (!isAuthenticated && !isPublicPath) {
    const url = request.nextUrl.clone();
    url.pathname = buildPath(locale, '/login');
    return NextResponse.redirect(url);
  }

  if (isAuthenticated && isPublicPath) {
    const url = request.nextUrl.clone();
    url.pathname = buildPath(locale, '/dashboard');
    return NextResponse.redirect(url);
  }

  return intlMiddleware(request);
}

export const config = {
  // Match all pathnames except API routes, Next.js internals, and static assets
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|icons|images).*)'],
};
