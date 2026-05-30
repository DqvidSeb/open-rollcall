import { Header } from '@/components/layout/Header/Header';
import { Sidebar } from '@/components/layout/Sidebar/Sidebar';

/**
 * Dashboard shell layout.
 *
 * Visual structure:
 *
 *  ┌──────────────────────────────────────────────┐  ← outer div: --layout-bg
 *  │ Sidebar │  Header (same --layout-bg)          │
 *  │         ╔══════════════════════════════════════╗  ← main: --page-bg
 *  │         ║  rounded top-left corner (20px)      ║
 *  │         ║  Page content fills here             ║
 *  │         ║                                      ║
 *  └─────────╚══════════════════════════════════════╝
 *
 * The outer div and sidebar/header share --layout-bg, creating the "frame".
 * The main content pane uses --page-bg + border-top-left-radius --page-radius.
 * Bottom and right edges touch the screen → those corners stay square naturally.
 */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: 'var(--layout-bg)' }}
    >
      <Sidebar />

      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />

        {/* Page content — different bg + only top-left rounded */}
        <main
          className="flex-1 overflow-y-auto p-6"
          style={{
            background:              'var(--page-bg)',
            borderTopLeftRadius:     'var(--page-radius)',
          }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
