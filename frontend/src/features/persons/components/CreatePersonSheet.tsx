'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { X } from '@phosphor-icons/react';
import { Input } from '@/components/ui/Input/Input';
import { Button } from '@/components/ui/Button/Button';
import { ApiError } from '@/lib/api/client';
import { personsService } from '../services/persons.service';
import { Field, selectClassName } from './formFields';
import type { EmployeeStatus, OptionItem, PersonType, StudentStatus } from '../types';

interface CreatePersonSheetProps {
  open: boolean;
  onClose: () => void;
  /** Called after the person was created successfully. */
  onCreated: () => void;
}

const initialState = {
  personType:    'employee' as PersonType,
  firstName:     '',
  lastName:      '',
  email:         '',
  phone:         '',
  code:          '',
  groupId:       '',
  positionId:    '',
  gradeLevel:    '',
  status:        'active' as EmployeeStatus | StudentStatus,
  date:          '',
};

export function CreatePersonSheet({ open, onClose, onCreated }: CreatePersonSheetProps) {
  const t = useTranslations('Persons.form');
  const tType = useTranslations('Persons.type');

  const [form, setForm]       = useState(initialState);
  const [departments, setDepartments] = useState<OptionItem[]>([]);
  const [positions, setPositions]     = useState<OptionItem[]>([]);
  const [programs, setPrograms]       = useState<OptionItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset the form whenever the sheet is opened.
  useEffect(() => {
    if (!open) return;
    setForm(initialState);
    setError(null);
  }, [open]);

  // Load select options once when the sheet opens.
  useEffect(() => {
    if (!open) return;
    personsService.listDepartments().then(setDepartments).catch(() => setDepartments([]));
    personsService.listPositions().then(setPositions).catch(() => setPositions([]));
    personsService.listAcademicPrograms().then(setPrograms).catch(() => setPrograms([]));
  }, [open]);

  // Reset the status field whenever the person type changes.
  const handlePersonTypeChange = (personType: PersonType) => {
    setForm(prev => ({ ...prev, personType, status: 'active', groupId: '', positionId: '', gradeLevel: '', code: '', date: '' }));
  };

  const update = (field: keyof typeof initialState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm(prev => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (form.personType === 'employee') {
        await personsService.createEmployee({
          first_name:    form.firstName,
          last_name:     form.lastName,
          email:         form.email || null,
          phone:         form.phone || null,
          employee_code: form.code,
          department_id: form.groupId || null,
          position_id:   form.positionId || null,
          status:        form.status as EmployeeStatus,
          hire_date:     form.date || null,
        });
      } else {
        await personsService.createStudent({
          first_name:          form.firstName,
          last_name:           form.lastName,
          email:               form.email || null,
          phone:               form.phone || null,
          student_code:        form.code,
          academic_program_id: form.groupId || null,
          grade_level:         form.gradeLevel || null,
          status:              form.status as StudentStatus,
          enrollment_date:     form.date || null,
        });
      }
      onCreated();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('errorGeneric'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const employeeStatuses: EmployeeStatus[] = ['active', 'inactive', 'on_leave'];
  const studentStatuses: StudentStatus[] = ['active', 'inactive', 'graduated', 'suspended'];
  const statusOptions = form.personType === 'employee' ? employeeStatuses : studentStatuses;

  return (
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
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
        aria-labelledby="create-person-title"
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
            <h2 id="create-person-title" style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ct-primary)', letterSpacing: '-0.01em' }}>
              {t('createTitle')}
            </h2>
            <p style={{ fontSize: '12.5px', color: 'var(--ct-secondary)', marginTop: '2px' }}>
              {t('createDescription')}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
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

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

            {/* Person type selector */}
            <Field label={t('personTypeLabel')}>
              <div style={{ display: 'flex', gap: '8px' }}>
                {(['employee', 'student'] as PersonType[]).map(type => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => handlePersonTypeChange(type)}
                    style={{
                      flex:         1,
                      padding:      '8px 12px',
                      borderRadius: '8px',
                      fontSize:     '13.5px',
                      fontWeight:   600,
                      cursor:       'pointer',
                      border:       form.personType === type ? 'none' : '1px solid var(--input-border)',
                      background:   form.personType === type ? 'var(--rc-accent)' : 'var(--sf-raised)',
                      color:        form.personType === type ? 'var(--rc-ink)' : 'var(--ct-primary)',
                      transition:   'background 130ms ease, color 130ms ease',
                    }}
                  >
                    {tType(type)}
                  </button>
                ))}
              </div>
            </Field>

            {/* Common fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <Input
                label={t('firstNameLabel')}
                value={form.firstName}
                onChange={update('firstName')}
                required
              />
              <Input
                label={t('lastNameLabel')}
                value={form.lastName}
                onChange={update('lastName')}
                required
              />
            </div>

            <Input
              label={t('emailLabel')}
              type="email"
              value={form.email}
              onChange={update('email')}
            />

            <Input
              label={t('phoneLabel')}
              type="tel"
              value={form.phone}
              onChange={update('phone')}
            />

            {/* Type-specific fields */}
            {form.personType === 'employee' ? (
              <>
                <Input
                  label={t('employeeCodeLabel')}
                  value={form.code}
                  onChange={update('code')}
                  required
                />

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <Field label={t('departmentLabel')}>
                    <select className={selectClassName} value={form.groupId} onChange={update('groupId')}>
                      <option value="">{t('selectPlaceholder')}</option>
                      {departments.map(d => (
                        <option key={d.id} value={d.id}>{d.name}</option>
                      ))}
                    </select>
                  </Field>

                  <Field label={t('positionLabel')}>
                    <select className={selectClassName} value={form.positionId} onChange={update('positionId')}>
                      <option value="">{t('selectPlaceholder')}</option>
                      {positions.map(p => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                      ))}
                    </select>
                  </Field>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <Field label={t('statusLabel')}>
                    <select className={selectClassName} value={form.status} onChange={update('status')}>
                      {statusOptions.map(s => (
                        <option key={s} value={s}>{t(`status.${s}`)}</option>
                      ))}
                    </select>
                  </Field>

                  <Input
                    label={t('hireDateLabel')}
                    type="date"
                    value={form.date}
                    onChange={update('date')}
                  />
                </div>
              </>
            ) : (
              <>
                <Input
                  label={t('studentCodeLabel')}
                  value={form.code}
                  onChange={update('code')}
                  required
                />

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <Field label={t('academicProgramLabel')}>
                    <select className={selectClassName} value={form.groupId} onChange={update('groupId')}>
                      <option value="">{t('selectPlaceholder')}</option>
                      {programs.map(p => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                      ))}
                    </select>
                  </Field>

                  <Input
                    label={t('gradeLevelLabel')}
                    value={form.gradeLevel}
                    onChange={update('gradeLevel')}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <Field label={t('statusLabel')}>
                    <select className={selectClassName} value={form.status} onChange={update('status')}>
                      {statusOptions.map(s => (
                        <option key={s} value={s}>{t(`status.${s}`)}</option>
                      ))}
                    </select>
                  </Field>

                  <Input
                    label={t('enrollmentDateLabel')}
                    type="date"
                    value={form.date}
                    onChange={update('date')}
                  />
                </div>
              </>
            )}

            {error && (
              <p style={{ fontSize: '13px', color: '#dc2626' }}>{error}</p>
            )}
          </div>

          {/* Footer */}
          <div
            style={{
              display:      'flex',
              justifyContent: 'flex-end',
              gap:          '10px',
              padding:      '16px 24px',
              borderTop:    '1px solid var(--sf-border)',
              flexShrink:   0,
            }}
          >
            <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>
              {t('cancelButton')}
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting}>
              {isSubmitting ? t('submittingButton') : t('submitButton')}
            </Button>
          </div>
        </form>
      </div>
    </>
  );
}
