import type { Metadata } from 'next';
import { Plus_Jakarta_Sans, Space_Grotesk } from 'next/font/google';
import { ThemeProvider } from '@/lib/theme/ThemeProvider';
import './globals.css';

/**
 * Plus Jakarta Sans — closest free equivalent to Neue Montreal.
 * Geometric humanist sans, clean and modern, great for SaaS UIs.
 * Loaded with Regular (400), Medium (500), SemiBold (600).
 */
const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jakarta',
  display: 'swap',
});

/** Space Grotesk Bold — ROLLCALL wordmark only */
const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  weight: ['700'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Roll Call',
  description: 'Facial recognition attendance system',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${jakarta.variable} ${spaceGrotesk.variable}`}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
