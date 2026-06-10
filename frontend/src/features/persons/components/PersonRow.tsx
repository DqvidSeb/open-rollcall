'use client';

import { useTranslations } from 'next-intl';
import { RoundCheckbox } from './RoundCheckbox';
import type { Person } from '../types';

interface PersonRowProps {
  person:   Person;
  selected: boolean;
  onSelect: (id: string, checked: boolean) => void;
  onClick:  (person: Person) => void;
}

/** Formats an ISO datetime string to a human-readable short date */
function fmtDate(iso: string): string {
  return new Intl.DateTimeFormat('en', {
    day:   '2-digit',
    month: 'short',
    year:  'numeric',
  }).format(new Date(iso));
}

export function PersonRow({ person, selected, onSelect, onClick }: PersonRowProps) {
  const t = useTranslations('Persons');

  return (
    <tr onClick={() => onClick(person)}>
      {/* ── Checkbox ── */}
      <td>
        <RoundCheckbox
          checked={selected}
          onChange={c => onSelect(person.id, c)}
          ariaLabel={`Select ${person.full_name}`}
        />
      </td>

      {/* ── Name — primary text ── */}
      <td>
        <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
          {person.full_name}
        </span>
      </td>

      {/* ── Type — primary, badge-style ── */}
      <td>
        {person.person_type ? (
          <span style={{ color: 'var(--tbl-primary)', fontWeight: 500 }}>
            {t(`type.${person.person_type}`)}
          </span>
        ) : (
          <span style={{ color: 'var(--tbl-secondary)', opacity: 0.45 }}>—</span>
        )}
      </td>

      {/* ── Code — secondary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)' }}>
          {person.code ?? '—'}
        </span>
      </td>

      {/* ── Group (department / academic program) — secondary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)' }}>
          {person.group_name ?? '—'}
        </span>
      </td>

      {/* ── Email — secondary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)' }}>
          {person.email ?? '—'}
        </span>
      </td>

      {/* ── Created date — tertiary ── */}
      <td>
        <span style={{ color: 'var(--tbl-secondary)', fontSize: '12.5px' }}>
          {fmtDate(person.created_at)}
        </span>
      </td>
    </tr>
  );
}
