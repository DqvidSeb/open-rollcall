import type { Config } from 'tailwindcss';

/**
 * Roll Call design tokens — Tailwind layer
 *
 * Raw palette:  rc.*
 * Semantic:     sidebar.* / header.* / surface.* / text.*
 *               These reference CSS custom properties defined in globals.css,
 *               so they adapt automatically to light / dark mode.
 */
const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/features/**/*.{js,ts,jsx,tsx,mdx}',
  ],

  theme: {
    extend: {
      // ── Raw palette ────────────────────────────────────────────────────
      colors: {
        rc: {
          accent: '#FF6D29',   // Orange  — CTAs, active states, logo
          brown:  '#453027',   // Brown   — dark surfaces, dark dividers
          ink:    '#161316',   // Near-black — darkest bg, dark text
          gray:   '#BABABA',   // Mid gray   — secondary text / borders
          white:  '#FFFFFF',   // Pure white
        },

        // ── Semantic tokens (CSS var–backed, theme-aware) ──────────────
        sidebar: {
          bg:           'var(--sb-bg)',
          border:       'var(--sb-border)',
          text:         'var(--sb-text)',
          muted:        'var(--sb-muted)',
          'active-bg':  'var(--sb-active-bg)',
          'active-text':'var(--sb-active-text)',
          'hover-bg':   'var(--sb-hover-bg)',
          'hover-text': 'var(--sb-hover-text)',
          divider:      'var(--sb-divider)',
        },
        header: {
          bg:     'var(--hd-bg)',
          border: 'var(--hd-border)',
          text:   'var(--hd-text)',
          muted:  'var(--hd-muted)',
        },
        surface: {
          base:   'var(--sf-base)',    // page/app background
          raised: 'var(--sf-raised)',  // cards, panels
          border: 'var(--sf-border)',
        },
        content: {
          primary:   'var(--ct-primary)',
          secondary: 'var(--ct-secondary)',
          disabled:  'var(--ct-disabled)',
        },
        accent: {
          DEFAULT: '#FF6D29',
          hover:   '#e85c1a',
          subtle:  'var(--ac-subtle)',   // low-opacity tint of accent
        },
      },

      // ── Typography ─────────────────────────────────────────────────────
      fontFamily: {
        // Plus Jakarta Sans → closest free equiv of Neue Montreal
        sans:   ['var(--font-jakarta)', 'Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        ui:     ['var(--font-jakarta)', 'Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        // Space Grotesk → ROLLCALL wordmark only
        display:['var(--font-space-grotesk)', 'Space Grotesk', 'system-ui', 'sans-serif'],
      },

      fontWeight: {
        regular:  '400',
        medium:   '500',
        semibold: '600',
      },

      // ── Radii ──────────────────────────────────────────────────────────
      borderRadius: {
        nav:    '6px',
        card:   '10px',
        dialog: '14px',
      },

      // ── Shadows ────────────────────────────────────────────────────────
      boxShadow: {
        'nav-active': '0 1px 3px rgba(255,109,41,0.20)',
        'card':       '0 1px 4px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.06)',
      },
    },
  },
  plugins: [],
};

export default config;
