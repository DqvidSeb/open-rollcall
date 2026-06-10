'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button/Button';
import { ApiError } from '@/lib/api/client';
import { departmentsService } from '../services/departments.service';
import { DeleteConfirmModal } from './DeleteConfirmModal';
import { DepartmentDetailsHeader } from './DepartmentDetailsHeader';
import { DepartmentFormFields } from './DepartmentFormFields';
import { DepartmentSheetShell } from './DepartmentSheetShell';
import type { Department } from '../types';

interface DepartmentDetailsSheetProps {
  open: boolean;
  department: Department | null;
  onClose: () => void;
  /** Called after the department was updated successfully. */
  onUpdated: () => void;
  /** Called after the department was deleted successfully. */
  onDeleted: () => void;
}

interface FormState {
  name:        string;
  description: string;
}

const emptyForm: FormState = { name: '', description: '' };

export function DepartmentDetailsSheet({ open, department, onClose, onUpdated, onDeleted }: DepartmentDetailsSheetProps) {
  const t = useTranslations('Departments.form');

  const [form, setForm]       = useState<FormState>(emptyForm);
  const [initial, setInitial] = useState<FormState>(emptyForm);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving]   = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset the form whenever the sheet opens for a new department.
  useEffect(() => {
    if (!open || !department) return;

    setIsEditing(false);
    setError(null);

    const next: FormState = {
      name:        department.name,
      description: department.description ?? '',
    };
    setForm(next);
    setInitial(next);
  }, [open, department]);

  const update = (field: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const isDirty = JSON.stringify(form) !== JSON.stringify(initial);

  const handleClose = () => {
    setIsEditing(false);
    onClose();
  };

  const handleSave = async () => {
    if (!department) return;
    setIsSaving(true);
    setError(null);

    try {
      const patch: Record<string, string | null> = {};
      if (form.name        !== initial.name)        patch.name        = form.name;
      if (form.description !== initial.description) patch.description = form.description || null;

      if (Object.keys(patch).length > 0) {
        await departmentsService.update(department.id, patch);
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
    if (!department) return;
    setIsDeleting(true);
    try {
      await departmentsService.delete(department.id);
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
      <DepartmentSheetShell open={open} onClose={handleClose} labelledBy="department-details-title">
        {/* Header */}
        <DepartmentDetailsHeader
          department={department}
          isEditing={isEditing}
          onEdit={() => setIsEditing(true)}
          onDelete={() => setShowDeleteConfirm(true)}
          onClose={handleClose}
        />

        {/* Form */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <DepartmentFormFields
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
      </DepartmentSheetShell>

      <DeleteConfirmModal
        open={showDeleteConfirm}
        isDeleting={isDeleting}
        onCancel={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
      />
    </>
  );
}
