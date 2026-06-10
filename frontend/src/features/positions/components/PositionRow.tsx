'use client';

import { RoundCheckbox } from './RoundCheckbox';
import type { Position } from '../types';

interface PositionRowProps {
  position:  Position;
  selected:  boolean;
  onSelect:  (id: string, checked: boolean) => void;
  onClick:   (position: Position) => void;
}

/** Formats an ISO datetime string to a human-readable short date */
function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('en', {
    day:   '2-digit',
    month: 'short',
    year:  'numeric',
  }).format(new Date(iso));
}

export function PositionRow({ position, selected, onSelect, onClick }: PositionRowProps) {
  return (
    <tr onClick={() => onClick(position)}>
      {/* ── Checkbox ── */}
      <td>
        <RoundCheckbox
          checked={selected}
          onChange={c => onSelect(position.id, c)}
          ariaLabel={`Select ${position.name}`}
        />
      </td>

      {/* ── Name — primary text ── */}
      <td>
        <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
          {position.name}
        </span>
      </td>

      {/* ── Description — secondary text ── */}
      <td style={{ maxWidth: '340px' }}>
        {position.description ? (
          <span
            style={{
              color:        'var(--tbl-secondary)',
              overflow:     'hidden',
              textOverflow: 'ellipsis',
              display:      'block',
              maxWidth:     '320px',
            }}
          >
            {position.description}
          </span>
        ) : (
          <span style={{ color: 'var(--tbl-secondary)', opacity: 0.45 }}>—</span>
        )}
      </td>

      {/* ── Created date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(position.created_at)}
        </span>
      </td>

      {/* ── Updated date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(position.updated_at)}
        </span>
      </td>
    </tr>
  );
}
