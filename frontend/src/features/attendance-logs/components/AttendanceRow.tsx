'use client';

import { useTranslations } from 'next-intl';
import { RoundCheckbox } from './RoundCheckbox';
import type { AttendanceLogItem } from '../types';

interface AttendanceRowProps {
  record:   AttendanceLogItem;
  selected: boolean;
  onSelect: (id: string, checked: boolean) => void;
}

/** Formats an ISO datetime string to a human-readable short date + time */
function fmtDateTime(iso: string): string {
  return new Intl.DateTimeFormat('en', {
    day:    '2-digit',
    month:  'short',
    year:   'numeric',
    hour:   '2-digit',
    minute: '2-digit',
  }).format(new Date(iso));
}

export function AttendanceRow({ record, selected, onSelect }: AttendanceRowProps) {
  const t = useTranslations('Attendance');

  const group = record.person_type === 'employee'
    ? record.department
    : record.person_type === 'student'
      ? record.academic_program
      : null;

  return (
    <tr>
      {/* ── Checkbox ── */}
      <td>
        <RoundCheckbox
          checked={selected}
          onChange={c => onSelect(record.id, c)}
          ariaLabel={`Select ${record.full_name ?? record.id}`}
        />
      </td>

      {/* ── Name — primary text ── */}
      <td>
        <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
          {record.full_name ?? '—'}
        </span>
      </td>

      {/* ── Type — primary, badge-style ── */}
      <td>
        {record.person_type ? (
          <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
            {t(`type.${record.person_type}`)}
          </span>
        ) : (
          <span style={{ color: 'var(--tbl-secondary)', opacity: 0.45 }}>—</span>
        )}
      </td>

      {/* ── Code — secondary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)' }}>
          {record.code ?? '—'}
        </span>
      </td>

      {/* ── Group (department / academic program) — secondary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)' }}>
          {group ?? '—'}
        </span>
      </td>

      {/* ── Event type — badge-style ── */}
      <td>
        <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
          {t(`eventType.${record.event_type}`)}
        </span>
      </td>

      {/* ── Method — secondary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)' }}>
          {t(`method.${record.method}`)}
        </span>
      </td>

      {/* ── Event time — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDateTime(record.event_time)}
        </span>
      </td>
    </tr>
  );
}
