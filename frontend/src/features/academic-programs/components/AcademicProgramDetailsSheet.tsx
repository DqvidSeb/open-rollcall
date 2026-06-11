'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button/Button';
import { ApiError } from '@/lib/api/client';
import { academicProgramsService } from '../services/academicPrograms.service';
import { DeleteConfirmModal } from './DeleteConfirmModal';
import { AcademicProgramDetailsHeader } from './AcademicProgramDetailsHeader';
import { AcademicProgramFormFields } from './AcademicProgramFormFields';
import { AcademicProgramSheetShell } from './AcademicProgramSheetShell';
import type { AcademicProgram } from '../types';

interface AcademicProgramDetailsSheetProps {
  open: boolean;
  program: AcademicProgram | null;
  onClose: () => void;
  /** Called after the academic program was updated successfully. */
  onUpdated: () => void;
  /** Called after the academic program was deleted successfully. */
  onDeleted: () => void;
}

interface FormState {
  name:        string;
  description: string;
}

const emptyForm: FormState = { name: '', description: '' };

export function AcademicProgramDetailsSheet({ open, program, onClose, onUpdated, onDeleted }: AcademicProgramDetailsSheetProps) {
  const t = useTranslations('AcademicPrograms.form');

  const [form, setForm]       = useState<FormState>(emptyForm);
  const [initial, setInitial] = useState<FormState>(emptyForm);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving]   = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset the form whenever the sheet opens for a new academic program.
  useEffect(() => {
    if (!open || !program) return;

    setIsEditing(false);
    setError(null);

    const next: FormState = {
      name:        program.name,
      description: program.description ?? '',
    };
    setForm(next);
    setInitial(next);
  }, [open, program]);

  const update = (field: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const isDirty = JSON.stringify(form) !== JSON.stringify(initial);

  const handleClose = () => {
    setIsEditing(false);
    onClose();
  };

  const handleSave = async () => {
    if (!program) return;
    setIsSaving(true);
    setError(null);

    try {
      const patch: Record<string, string | null> = {};
      if (form.name        !== initial.name)        patch.name        = form.name;
      if (form.description !== initial.description) patch.description = form.description || null;

      if (Object.keys(patch).length > 0) {
        await academicProgramsService.update(program.id, patch);
      }

      setInitial(form);
      setIsEditing(false);
      onUpdated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('errorGeneric'));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!program) return;
    setIsDeleting(true);
    try {
      await academicProgramsService.delete(program.id);
      setShowDeleteConfirm(false);
      onDeleted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('errorGeneric'));
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const fieldsDisabled = !isEditing;

  return (
    <>
      <AcademicProgramSheetShell open={open} onClose={handleClose} labelledBy="academic-program-details-title">
        {/* Header */}
        <AcademicProgramDetailsHeader
          program={program}
          isEditing={isEditing}
          onEdit={() => setIsEditing(true)}
          onDelete={() => setShowDeleteConfirm(true)}
          onClose={handleClose}
        />

        {/* Form */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <AcademicProgramFormFields
            name={form.name}
            description={form.description}
            onChangeName={update('name')}
            onChangeDescription={update('description')}
            disabled={fieldsDisabled}
            error={error}
          />
        </div>

        {/* Footer */}
        {isEditing && (
          <div
            style={{
              display:        'flex',
              justifyContent: 'flex-end',
              gap:            '10px',
              padding:        '16px 24px',
              borderTop:      '1px solid var(--sf-border)',
              flexShrink:     0,
            }}
          >
            <Button
              type="button"
              variant="secondary"
              onClick={() => { setForm(initial); setIsEditing(false); setError(null); }}
              disabled={isSaving}
            >
              {t('cancelButton')}
            </Button>
            <Button
              type="button"
              variant="primary"
              onClick={handleSave}
              disabled={!isDirty || isSaving}
              isLoading={isSaving}
            >
              {isSaving ? t('savingButton') : t('saveButton')}
            </Button>
          </div>
        )}
      </AcademicProgramSheetShell>

      <DeleteConfirmModal
        open={showDeleteConfirm}
        isDeleting={isDeleting}
        onCancel={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
      />
    </>
  );
}
