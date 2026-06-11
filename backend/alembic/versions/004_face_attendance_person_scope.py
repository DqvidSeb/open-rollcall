"""Generalize face_encoding and attendance_log to reference person

Revision ID: 004
Revises: 003
Create Date: 2026-06-10

Motivación:
  · `face_encoding` y `attendance_log` apuntaban únicamente a `employee.id`,
    por lo que el reconocimiento facial y el registro de asistencia solo
    funcionaban para empleados.
  · `Employee.id` y `Student.id` son ambos el mismo UUID que `Person.id`
    (especialización 1:1), así que retargetear la FK a `person.id` no
    requiere migrar datos: los valores existentes siguen siendo válidos.
  · A partir de esta migración, cualquier `Person` que sea `employee` o
    `student` puede tener encodings faciales y registros de asistencia.
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── face_encoding: employee_id -> person_id ──────────────────────────────
    op.alter_column("face_encoding", "employee_id", new_column_name="person_id")
    op.drop_constraint("face_encoding_employee_id_fkey", "face_encoding", type_="foreignkey")
    op.create_foreign_key(
        "face_encoding_person_id_fkey",
        "face_encoding", "person",
        ["person_id"], ["id"],
        ondelete="CASCADE",
    )
    op.drop_index("ix_face_encoding_employee_id", table_name="face_encoding")
    op.create_index("ix_face_encoding_person_id", "face_encoding", ["person_id"])

    # ── attendance_log: employee_id -> person_id ─────────────────────────────
    op.alter_column("attendance_log", "employee_id", new_column_name="person_id")
    op.drop_constraint("attendance_log_employee_id_fkey", "attendance_log", type_="foreignkey")
    op.create_foreign_key(
        "attendance_log_person_id_fkey",
        "attendance_log", "person",
        ["person_id"], ["id"],
        ondelete="CASCADE",
    )
    op.drop_index("ix_attendance_log_employee_id", table_name="attendance_log")
    op.create_index("ix_attendance_log_person_id", "attendance_log", ["person_id"])


def downgrade() -> None:
    # ── attendance_log: person_id -> employee_id ─────────────────────────────
    op.drop_index("ix_attendance_log_person_id", table_name="attendance_log")
    op.drop_constraint("attendance_log_person_id_fkey", "attendance_log", type_="foreignkey")
    op.alter_column("attendance_log", "person_id", new_column_name="employee_id")
    op.create_foreign_key(
        "attendance_log_employee_id_fkey",
        "attendance_log", "employee",
        ["employee_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_attendance_log_employee_id", "attendance_log", ["employee_id"])

    # ── face_encoding: person_id -> employee_id ──────────────────────────────
    op.drop_index("ix_face_encoding_person_id", table_name="face_encoding")
    op.drop_constraint("face_encoding_person_id_fkey", "face_encoding", type_="foreignkey")
    op.alter_column("face_encoding", "person_id", new_column_name="employee_id")
    op.create_foreign_key(
        "face_encoding_employee_id_fkey",
        "face_encoding", "employee",
        ["employee_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_face_encoding_employee_id", "face_encoding", ["employee_id"])
