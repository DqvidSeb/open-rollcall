'use client';

import { useState } from 'react';
import { PositionsToolbar } from './PositionsToolbar';
import { PositionsTable } from './PositionsTable';
import { CreatePositionSheet } from './CreatePositionSheet';
import { PositionDetailsSheet } from './PositionDetailsSheet';
import type { Position } from '../types';

/**
 * Client-side shell for the Positions page.
 *
 * Owns the "create position" and "position details" sheet state and
 * forces the table to refetch (via remount) after a position is created,
 * updated or deleted.
 */
export function PositionsPageContent() {
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = () => setRefreshKey(k => k + 1);

  return (
    <div className="flex flex-col gap-5">
      <PositionsToolbar onAdd={() => setCreateOpen(true)} />
      <PositionsTable key={refreshKey} onRowClick={setSelectedPosition} />

      <CreatePositionSheet
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={refresh}
      />

      <PositionDetailsSheet
        open={selectedPosition !== null}
        position={selectedPosition}
        onClose={() => setSelectedPosition(null)}
        onUpdated={refresh}
        onDeleted={() => { setSelectedPosition(null); refresh(); }}
      />
    </div>
  );
}
