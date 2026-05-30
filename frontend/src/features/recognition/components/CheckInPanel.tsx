// CheckInPanel — stub, to be implemented
// Live feed of recognized students + manual override
'use client';

import { useTranslations } from 'next-intl';

export function CheckInPanel() {
  const t = useTranslations('Recognition');

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-base font-semibold text-gray-800">{t('recentCheckIns')}</h2>
      {/* TODO: list of RecognitionResult items, manual check-in button */}
    </div>
  );
}
