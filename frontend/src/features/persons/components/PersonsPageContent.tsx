'use client';

import { useState } from 'react';
import { PersonsToolbar } from './PersonsToolbar';
import { PersonsTable } from './PersonsTable';
import { CreatePersonSheet } from './CreatePersonSheet';
import { PersonDetailsSheet } from './PersonDetailsSheet';
import type { Person } from '../types';

/**
 * Client-side shell for the Persons page.
 *
 * Owns the "create person" and "person details" sheet state and forces
 * the table to refetch (via remount) after a person is created, updated
 * or deleted.
 */
export function PersonsPageContent() {
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = () => setRefreshKey(k => k + 1);

  return (
    <div className="flex flex-col gap-5">
      <PersonsToolbar onAdd={() => setCreateOpen(true)} />
      <PersonsTable key={refreshKey} onRowClick={setSelectedPerson} />

      <CreatePersonSheet
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={refresh}
      />

      <PersonDetailsSheet
        open={selectedPerson !== null}
        person={selectedPerson}
        onClose={() => setSelectedPerson(null)}
        onUpdated={refresh}
        onDeleted={() => { setSelectedPerson(null); refresh(); }}
      />
    </div>
  );
}
