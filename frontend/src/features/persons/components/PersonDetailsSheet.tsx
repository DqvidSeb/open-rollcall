'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { X, PencilSimple, Trash } from '@phosphor-icons/react';
import { Input } from '@/components/ui/Input/Input';
import { Button } from '@/components/ui/Button/Button';
import { ApiError } from '@/lib/api/client';
import { personsService } from '../services/persons.service';
import { Field, selectClassName } from './formFields';
import { DeleteConfirmModal } from './DeleteConfirmModal';
import { FaceEnrollmentSection } from '@/features/face-enrollment/components/FaceEnrollmentSection';
import type { EmployeeStatus, OptionItem, Person, StudentStatus } from '../types';

interface PersonDetailsSheetProps {
  open: boolean;
  person: Person | null;
  onClose: () => void;
  /** Called after the person was updated successfully. */
  onUpdated: () => void;
  /** Called after the person was deleted successfully. */
  onDeleted: () => void;
}

interface FormState {
  firstName:  string;
  lastName:   string;
  email:      string;
  phone:      string;
  code:       string;
  groupId:    string;
  positionId: string;
  gradeLevel: string;
  status:     EmployeeStatus | StudentStatus | '';
  date:       string;
}

const emptyForm: FormState = {
  firstName: '', lastName: '', email: '', phone: '',
  code: '', groupId: '', positionId: '', gradeLevel: '', status: '', date: '',
};

export function PersonDetailsSheet({ open, person, onClose, onUpdated, onDeleted }: PersonDetailsSheetProps) {
  const t = useTranslations('Persons.form');
  const tType = useTranslations('Persons.type');

  const [form, setForm]         = useState<FormState>(emptyForm);
  const [initial, setInitial]   = useState<FormState>(emptyForm);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving]   = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [departments, setDepartments] = useState<OptionItem[]>([]);
  const [positions, setPositions]     = useState<OptionItem[]>([]);
  const [programs, setPrograms]       = useState<OptionItem[]>([]);

  const personType = person?.person_type ?? null;

  // Load the person's full details whenever the sheet opens for a new person.
  useEffect(() => {
    if (!open || !person) return;

    setIsEditing(false);
    setError(null);
    setIsLoading(true);

    personsService.listDepartments().then(setDepartments).catch(() => setDepartments([]));
    personsService.listPositions().then(setPositions).catch(() => setPositions([]));
    personsService.listAcademicPrograms().then(setPrograms).catch(() => setPrograms([]));

    const load = async () => {
      try {
        const base = await personsService.getPerson(person.id);
        let next: FormState = {
          ...emptyForm,
          firstName: base.first_name,
          lastName:  base.last_name,
          email:     base.email ?? '',
          phone:     base.phone ?? '',
        };

        if (personType === 'employee') {
          const emp = await personsService.getEmployee(person.id);
          next = {
            ...next,
            code:       emp.employee_code,
            groupId:    emp.department_id ?? '',
            positionId: emp.position_id ?? '',
            status:     emp.status,
            date:       emp.hire_date ?? '',
          };
        } else if (personType === 'student') {
          const stu = await personsService.getStudent(person.id);
          next = {
            ...next,
            code:       stu.student_code,
            groupId:    stu.academic_program_id ?? '',
            gradeLevel: stu.grade_level ?? '',
            status:     stu.status,
            date:       stu.enrollment_date ?? '',
          };
        }

        setForm(next);
        setInitial(next);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : t('errorGeneric'));
      } finally {
        setIsLoading(false);
      }
    };

    load();
    // `t` from next-intl is recreated every render; including it would re-trigger this load effect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, person, personType]);

  const update = (field: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const isDirty = JSON.stringify(form) !== JSON.stringify(initial);

  const handleClose = () => {
    setIsEditing(false);
    onClose();
  };

  const handleSave = async () => {
    if (!person) return;
    setIsSaving(true);
    setError(null);

    try {
      const personPatch: Record<string, string | null> = {};
      if (form.firstName !== initial.firstName) personPatch.first_name = form.firstName;
      if (form.lastName  !== initial.lastName)  personPatch.last_name  = form.lastName;
      if (form.email     !== initial.email)     personPatch.email      = form.email || null;
      if (form.phone     !== initial.phone)     personPatch.phone      = form.phone || null;

      if (Object.keys(personPatch).length > 0) {
        await personsService.updatePerson(person.id, personPatch);
      }

      if (personType === 'employee') {
        const patch: Record<string, string | null> = {};
        if (form.groupId    !== initial.groupId)    patch.department_id = form.groupId || null;
        if (form.positionId !== initial.positionId) patch.position_id   = form.positionId || null;
        if (form.status     !== initial.status)     patch.status        = form.status as EmployeeStatus;
        if (form.date       !== initial.date)       patch.hire_date     = form.date || null;

        if (Object.keys(patch).length > 0) {
          await personsService.updateEmployee(person.id, patch);
        }
      } else if (personType === 'student') {
        const patch: Record<string, string | null> = {};
        if (form.groupId    !== initial.groupId)    patch.academic_program_id = form.groupId || null;
        if (form.gradeLevel !== initial.gradeLevel) patch.grade_level         = form.gradeLevel || null;
        if (form.status     !== initial.status)     patch.status              = form.status as StudentStatus;
        if (form.date       !== initial.date)       patch.enrollment_date     = form.date || null;

        if (Object.keys(patch).length > 0) {
          await personsService.updateStudent(person.id, patch);
        }
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
    if (!person) return;
    setIsDeleting(true);
    try {
      if (personType === 'employee') {
        await personsService.deleteEmployee(person.id);
      } else if (personType === 'student') {
        await personsService.deleteStudent(person.id);
      }
      setShowDeleteConfirm(false);
      onDeleted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('errorGeneric'));
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const employeeStatuses: EmployeeStatus[] = ['active', 'inactive', 'on_leave'];
  const studentStatuses: StudentStatus[] = ['active', 'inactive', 'graduated', 'suspended'];

  const fieldsDisabled = !isEditing || isLoading;

  return (
    <>
      {/* Overlay */}
      <div
        onClick={handleClose}
        style={{
          position:   'fixed',
          inset:      0,
          background: 'rgba(0, 0, 0, 0.45)',
          opacity:    open ? 1 : 0,
          pointerEvents: open ? 'auto' : 'none',
          transition: 'opacity 200ms ease',
          zIndex:     50,
        }}
        aria-hidden="true"
      />

      {/* Sheet */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="person-details-title"
        style={{
          position:   'fixed',
          top:        0,
          right:      0,
          bottom:     0,
          width:      'min(440px, 100vw)',
          background: 'var(--page-bg)',
          borderLeft: '1px solid var(--sf-border)',
          boxShadow:  '-8px 0 32px rgba(0, 0, 0, 0.18)',
          transform:  open ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 240ms ease',
          zIndex:     51,
          display:    'flex',
          flexDirection: 'column',
        }}
      >
        {/* Header */}
        <div
          style={{
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'space-between',
            padding:        '20px 24px',
            borderBottom:   '1px solid var(--sf-border)',
            flexShrink:     0,
          }}
        >
          <div>
            <h2 id="person-details-title" style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ct-primary)', letterSpacing: '-0.01em' }}>
              {person?.full_name ?? t('detailsTitle')}
            </h2>
            {personType && (
              <p style={{ fontSize: '12.5px', color: 'var(--ct-secondary)', marginTop: '2px' }}>
                {tType(personType)}
              </p>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <button
              type="button"
              onClick={() => setIsEditing(true)}
              disabled={isEditing || isLoading}
              aria-label={t('editButton')}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                width: '32px', height: '32px', borderRadius: '9999px', border: 'none',
                background: 'transparent', color: 'var(--ct-secondary)',
                cursor: isEditing || isLoading ? 'default' : 'pointer',
                opacity: isEditing || isLoading ? 0.4 : 1,
                transition: 'background 130ms ease',
              }}
              onMouseEnter={e => { if (!isEditing && !isLoading) e.currentTarget.style.background = 'var(--ac-subtle)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              <PencilSimple size={17} weight="bold" />
            </button>

            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isLoading}
              aria-label={t('deleteButton')}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                width: '32px', height: '32px', borderRadius: '9999px', border: 'none',
                background: 'transparent', color: '#dc2626',
                cursor: isLoading ? 'default' : 'pointer',
                opacity: isLoading ? 0.4 : 1,
                transition: 'background 130ms ease',
              }}
              onMouseEnter={e => { if (!isLoading) e.currentTarget.style.background = 'rgba(220, 38, 38, 0.10)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              <Trash size={17} weight="bold" />
            </button>

            <button
              type="button"
              onClick={handleClose}
              aria-label={t('cancelButton')}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                width: '32px', height: '32px', borderRadius: '9999px', border: 'none',
                background: 'transparent', color: 'var(--ct-secondary)', cursor: 'pointer',
                transition: 'background 130ms ease',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'var(--ac-subtle)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              <X size={18} weight="bold" />
            </button>
          </div>
        </div>

        {/* Form */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <Input
              label={t('firstNameLabel')}
              value={form.firstName}
              onChange={update('firstName')}
              disabled={fieldsDisabled}
            />
            <Input
              label={t('lastNameLabel')}
              value={form.lastName}
              onChange={update('lastName')}
              disabled={fieldsDisabled}
            />
          </div>

          <Input
            label={t('emailLabel')}
            type="email"
            value={form.email}
            onChange={update('email')}
            disabled={fieldsDisabled}
          />

          <Input
            label={t('phoneLabel')}
            type="tel"
            value={form.phone}
            onChange={update('phone')}
            disabled={fieldsDisabled}
          />

          {personType === 'employee' && (
            <>
              <Input
                label={t('employeeCodeLabel')}
                value={form.code}
                disabled
                hint={t('codeImmutableHint')}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <Field label={t('departmentLabel')}>
                  <select className={selectClassName} value={form.groupId} onChange={update('groupId')} disabled={fieldsDisabled}>
                    <option value="">{t('noneOption')}</option>
                    {departments.map(d => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </Field>

                <Field label={t('positionLabel')}>
                  <select className={selectClassName} value={form.positionId} onChange={update('positionId')} disabled={fieldsDisabled}>
                    <option value="">{t('noneOption')}</option>
                    {positions.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </Field>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <Field label={t('statusLabel')}>
                  <select className={selectClassName} value={form.status} onChange={update('status')} disabled={fieldsDisabled}>
                    {employeeStatuses.map(s => (
                      <option key={s} value={s}>{t(`status.${s}`)}</option>
                    ))}
                  </select>
                </Field>

                <Input
                  label={t('hireDateLabel')}
                  type="date"
                  value={form.date}
                  onChange={update('date')}
                  disabled={fieldsDisabled}
                />
              </div>
            </>
          )}

          {personType === 'student' && (
            <>
              <Input
                label={t('studentCodeLabel')}
                value={form.code}
                disabled
                hint={t('codeImmutableHint')}
              />

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <Field label={t('academicProgramLabel')}>
                  <select className={selectClassName} value={form.groupId} onChange={update('groupId')} disabled={fieldsDisabled}>
                    <option value="">{t('noneOption')}</option>
                    {programs.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </Field>

                <Input
                  label={t('gradeLevelLabel')}
                  value={form.gradeLevel}
                  onChange={update('gradeLevel')}
                  disabled={fieldsDisabled}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <Field label={t('statusLabel')}>
                  <select className={selectClassName} value={form.status} onChange={update('status')} disabled={fieldsDisabled}>
                    {studentStatuses.map(s => (
                      <option key={s} value={s}>{t(`status.${s}`)}</option>
                    ))}
                  </select>
                </Field>

                <Input
                  label={t('enrollmentDateLabel')}
                  type="date"
                  value={form.date}
                  onChange={update('date')}
                  disabled={fieldsDisabled}
                />
              </div>
            </>
          )}

          {error && (
            <p style={{ fontSize: '13px', color: '#dc2626' }}>{error}</p>
          )}

          {person && (personType === 'employee' || personType === 'student') && (
            <FaceEnrollmentSection personType={personType} employeeId={person.id} />
          )}
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
      </div>

      <DeleteConfirmModal
        open={showDeleteConfirm}
        isDeleting={isDeleting}
        onCancel={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
      />
    </>
  );
}
