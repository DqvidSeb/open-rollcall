interface LogoProps {
  /** Width of the mark in px. Height = same (square). */
  size?: number;
  showText?: boolean;
  className?: string;
}

/**
 * Roll Call logo mark.
 *
 * Shape: 8-arm asterisk with chamfered inner corners — each pair of adjacent
 * arms is connected by a short diagonal notch instead of a sharp right-angle,
 * giving the iconic "rotary snowflake" look seen in the reference.
 *
 * Construction (viewBox 200 × 200, center 100 100):
 *   r_out = 84   arm outer radius
 *   r_in  = 20   inner radius (depth of chamfer)
 *   hw    = 13   arm half-width
 *
 * Each arm contributes 4 outline points; the 8 chamfer segments connect them.
 * Total: 32 vertices + 8 chamfer lines = one closed path, no overlap, no clip.
 *
 * Arms at 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315° (screen CW from east).
 * For arm at angle θ:
 *   axis        = (cos θ,  sin θ)
 *   perp_CW_scr = (sin θ, -cos θ)   ← CW perpendicular in screen coords
 *   outer_CW    = center + r_out·axis + hw·perp_CW_scr
 *   outer_CCW   = center + r_out·axis - hw·perp_CW_scr
 *   inner_CW    = center + r_in·axis  + hw·perp_CW_scr
 *   inner_CCW   = center + r_in·axis  - hw·perp_CW_scr
 * Chamfer between arm[i] and arm[i+1]: inner_CCW[i] → inner_CW[i+1]
 */
export function Logo({ size = 32, showText = true, className }: LogoProps) {
  return (
    <div className={`flex items-center gap-2.5 ${className ?? ''}`}>

      {/* ── Mark: 8-arm chamfered asterisk ──────────────────────── */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          fill="var(--rc-accent)"
          d="
            M 184 87
            L 184 113
            L 120 113
            L 123.33 104.95
            L 168.59 150.21
            L 150.21 168.59
            L 104.95 123.33
            L 113 120
            L 113 184
            L 87 184
            L 87 120
            L 95.05 123.33
            L 49.79 168.59
            L 31.41 150.21
            L 76.67 104.95
            L 80 113
            L 16 113
            L 16 87
            L 80 87
            L 76.67 95.05
            L 31.41 49.79
            L 49.79 31.41
            L 95.05 76.67
            L 87 80
            L 87 16
            L 113 16
            L 113 80
            L 104.95 76.67
            L 150.21 31.41
            L 168.59 49.79
            L 123.33 95.05
            L 120 87
            Z
          "
        />
      </svg>

      {/* ── Wordmark ─────────────────────────────────────────────── */}
      {showText && (
        <span
          className="font-display font-bold uppercase select-none"
          style={{
            fontSize:      `${Math.round(size * 0.66) + 2}px`,
            letterSpacing: '-0.02em',
            color:         'var(--ct-primary)',
          }}
        >
          Rollcall
        </span>
      )}
    </div>
  );
}
