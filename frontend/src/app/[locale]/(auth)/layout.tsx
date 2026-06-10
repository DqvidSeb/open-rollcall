// Auth route group layout — no sidebar/header, centered card on the
// themed page background (light/dark aware via --sf-base).
interface AuthLayoutProps {
  children: React.ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <main
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--sf-base)' }}
    >
      {children}
    </main>
  );
}
