// Auth route group layout — no sidebar/header, centered card
interface AuthLayoutProps {
  children: React.ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      {children}
    </main>
  );
}
