/**
 * Roll Call design tokens — JS/TS layer
 *
 * Single source of truth for values that need to be used in JS
 * (e.g., canvas drawing in recognition, chart colors, animations).
 *
 * Tailwind / CSS equivalents live in:
 *   - tailwind.config.ts  (utility classes)
 *   - src/app/globals.css (CSS custom properties)
 */

export const RC = {
  /** Raw palette */
  palette: {
    accent: '#FF6D29',
    brown:  '#453027',
    ink:    '#161316',
    gray:   '#BABABA',
    white:  '#FFFFFF',
  },

  /** Accent tints (for canvas overlays, chart fills, etc.) */
  accent: {
    solid:   '#FF6D29',
    hover:   '#E85C1A',
    tint12:  'rgba(255,109,41,0.12)',
    tint08:  'rgba(255,109,41,0.08)',
  },

  /** Typography scale */
  font: {
    ui:      "'Plus Jakarta Sans', system-ui, sans-serif",
    display: "'Space Grotesk', system-ui, sans-serif",
  },

  fontWeight: {
    regular:  400,
    medium:   500,
    semibold: 600,
    bold:     700,
  },

  /** Border radius */
  radius: {
    nav:    '6px',
    card:   '10px',
    dialog: '14px',
    full:   '9999px',
  },
} as const;

export type RCPalette = typeof RC.palette;
