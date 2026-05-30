'use client';

import { RoundCheckbox } from './RoundCheckbox';
import type { Department } from '../types';

interface DepartmentRowProps {
  dept:      Department;
  selected:  boolean;
  onSelect:  (id: string, checked: boolean) => void;
  onClick:   (dept: Department) => void;
}

/** Formats an ISO datetime string to a human-readable short date */
function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('en', {
    day:   '2-digit',
    month: 'short',
    year:  'numeric',
  }).format(new Date(iso));
}

export function DepartmentRow({ dept, selected, onSelect, onClick }: DepartmentRowProps) {
  return (
    <tr onClick={() => onClick(dept)}>
      {/* ── Checkbox ── */}
      <td>
        <RoundCheckbox
          checked={selected}
          onChange={c => onSelect(dept.id, c)}
          ariaLabel={`Select ${dept.name}`}
        />
      </td>

      {/* ── Name — primary text ── */}
      <td>
        <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
          {dept.name}
        </span>
      </td>

      {/* ── Description — secondary text ── */}
      <td style={{ maxWidth: '340px' }}>
        {dept.description ? (
          <span
            style={{
              color:        'var(--tbl-secondary)',
              overflow:     'hidden',
              textOverflow: 'ellipsis',
              display:      'block',
              maxWidth:     '320px',
            }}
          >
            {dept.description}
          </span>
        ) : (
          <span style={{ color: 'var(--tbl-secondary)', opacity: 0.45 }}>—</span>
        )}
      </td>

      {/* ── Created date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(dept.created_at)}
        </span>
      </td>

      {/* ── Updated date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(dept.updated_at)}
        </span>
      </td>
    </tr>
  );
}
