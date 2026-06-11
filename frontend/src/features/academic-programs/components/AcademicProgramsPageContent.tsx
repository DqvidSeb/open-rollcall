'use client';

import { useState } from 'react';
import { AcademicProgramsToolbar } from './AcademicProgramsToolbar';
import { AcademicProgramsTable } from './AcademicProgramsTable';
import { CreateAcademicProgramSheet } from './CreateAcademicProgramSheet';
import { AcademicProgramDetailsSheet } from './AcademicProgramDetailsSheet';
import type { AcademicProgram } from '../types';

/**
 * Client-side shell for the Academic Programs page.
 *
 * Owns the "create program" and "program details" sheet state and
 * forces the table to refetch (via remount) after a program is created,
 * updated or deleted.
 */
export function AcademicProgramsPageContent() {
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState<AcademicProgram | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = () => setRefreshKey(k => k + 1);

  return (
    <div className="flex flex-col gap-5">
      <AcademicProgramsToolbar onAdd={() => setCreateOpen(true)} />
      <AcademicProgramsTable key={refreshKey} onRowClick={setSelectedProgram} />

      <CreateAcademicProgramSheet
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={refresh}
      />

      <AcademicProgramDetailsSheet
        open={selectedProgram !== null}
        program={selectedProgram}
        onClose={() => setSelectedProgram(null)}
        onUpdated={refresh}
        onDeleted={() => { setSelectedProgram(null); refresh(); }}
      />
    </div>
  );
}
