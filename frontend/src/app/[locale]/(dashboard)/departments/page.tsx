import { DepartmentsToolbar } from '@/features/departments/components/DepartmentsToolbar';
import { DepartmentsTable } from '@/features/departments/components/DepartmentsTable';

/**
 * Departments page.
 *
 * No title — toolbar + table sit directly on the page surface.
 * No card wrappers, no extra backgrounds, no borders.
 */
export default function DepartmentsPage() {
  return (
    <div className="flex flex-col gap-5">
      <DepartmentsToolbar />
      <DepartmentsTable />
    </div>
  );
}
