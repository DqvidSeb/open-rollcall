'use client';

import { RoundCheckbox } from './RoundCheckbox';
import type { AcademicProgram } from '../types';

interface AcademicProgramRowProps {
  program:  AcademicProgram;
  selected: boolean;
  onSelect: (id: string, checked: boolean) => void;
  onClick:  (program: AcademicProgram) => void;
}

/** Formats an ISO datetime string to a human-readable short date */
function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('en', {
    day:   '2-digit',
    month: 'short',
    year:  'numeric',
  }).format(new Date(iso));
}

export function AcademicProgramRow({ program, selected, onSelect, onClick }: AcademicProgramRowProps) {
  return (
    <tr onClick={() => onClick(program)}>
      {/* ── Checkbox ── */}
      <td>
        <RoundCheckbox
          checked={selected}
          onChange={c => onSelect(program.id, c)}
          ariaLabel={`Select ${program.name}`}
        />
      </td>

      {/* ── Name — primary text ── */}
      <td>
        <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
          {program.name}
        </span>
      </td>

      {/* ── Description — secondary text ── */}
      <td style={{ maxWidth: '340px' }}>
        {program.description ? (
          <span
            style={{
              color:        'var(--tbl-secondary)',
              overflow:     'hidden',
              textOverflow: 'ellipsis',
              display:      'block',
              maxWidth:     '320px',
            }}
          >
            {program.description}
          </span>
        ) : (
          <span style={{ color: 'var(--tbl-secondary)', opacity: 0.45 }}>—</span>
        )}
      </td>

      {/* ── Created date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(program.created_at)}
        </span>
      </td>

      {/* ── Updated date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(program.updated_at)}
        </span>
      </td>
    </tr>
  );
}
