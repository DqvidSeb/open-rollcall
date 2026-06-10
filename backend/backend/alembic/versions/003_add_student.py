"""Add student and academic_program tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-10

Diseño normalizado (1FN – 3FN):
  · academic_program es un catálogo independiente (evita repetir el nombre
    del programa en cada fila de student — elimina dependencia transitiva).
  · student es una especialización 1:1 de person (misma PK, FK a person.id),
    análoga a employee. Cada columna depende únicamente de student.id.
  · No existen grupos repetitivos ni dependencias parciales.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE student_status AS ENUM ('active', 'inactive', 'graduated', 'suspended')")

    # ── academic_program ──────────────────────────────────────────────────────
    op.create_table(
        "academic_program",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_academic_program_name"),
    )

    # ── student ───────────────────────────────────────────────────────────────
    op.create_table(
        "student",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_code", sa.String(30), nullable=False),
        sa.Column("academic_program_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("grade_level", sa.String(30), nullable=True),
        sa.Column("status", postgresql.ENUM(name="student_status", create_type=False), nullable=False, server_default="active"),
        sa.Column("enrollment_date", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["id"], ["person.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["academic_program_id"], ["academic_program.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("student_code", name="uq_student_code"),
    )
    op.create_index("ix_student_code", "student", ["student_code"])
    op.create_index("ix_student_academic_program_id", "student", ["academic_program_id"])
    op.create_index("ix_student_status", "student", ["status"])

    for table in ("academic_program", "student"):
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
        """)


def downgrade() -> None:
    for table in ("academic_program", "student"):
        op.execute(f'DROP TRIGGER IF EXISTS trg_{table}_updated_at ON "{table}"')

    op.drop_table("student")
    op.drop_table("academic_program")

    op.execute("DROP TYPE IF EXISTS student_status")
