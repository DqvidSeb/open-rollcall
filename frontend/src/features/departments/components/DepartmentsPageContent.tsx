'use client';

import { useState } from 'react';
import { DepartmentsToolbar } from './DepartmentsToolbar';
import { DepartmentsTable } from './DepartmentsTable';
import { CreateDepartmentSheet } from './CreateDepartmentSheet';
import { DepartmentDetailsSheet } from './DepartmentDetailsSheet';
import type { Department } from '../types';

/**
 * Client-side shell for the Departments page.
 *
 * Owns the "create department" and "department details" sheet state and
 * forces the table to refetch (via remount) after a department is created,
 * updated or deleted.
 */
export function DepartmentsPageContent() {
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState<Department | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = () => setRefreshKey(k => k + 1);

  return (
    <div className="flex flex-col gap-5">
      <DepartmentsToolbar onAdd={() => setCreateOpen(true)} />
      <DepartmentsTable key={refreshKey} onRowClick={setSelectedDepartment} />

      <CreateDepartmentSheet
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={refresh}
      />

      <DepartmentDetailsSheet
        open={selectedDepartment !== null}
        department={selectedDepartment}
        onClose={() => setSelectedDepartment(null)}
        onUpdated={refresh}
        onDeleted={() => { setSelectedDepartment(null); refresh(); }}
      />
    </div>
  );
}
