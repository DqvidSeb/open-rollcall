"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Extensiones ───────────────────────────────────────────────────────────
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')   # gen_random_uuid()
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')     # pgvector

    # ── ENUMs ─────────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE employee_status AS ENUM ('active', 'inactive', 'on_leave')")
    op.execute("CREATE TYPE event_type AS ENUM ('check_in', 'check_out')")
    op.execute("CREATE TYPE attendance_method AS ENUM ('face_recognition', 'manual', 'override')")

    # ── person ────────────────────────────────────────────────────────────────
    op.create_table(
        "person",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("first_name", sa.String(80), nullable=False),
        sa.Column("last_name", sa.String(80), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name="uq_person_email"),
    )
    op.create_index("ix_person_email", "person", ["email"])
    op.create_index("ix_person_deleted_at", "person", ["deleted_at"])

    # ── user (palabra reservada → quoting explícito) ───────────────────────────
    op.execute("""
        CREATE TABLE "user" (
            id          UUID PRIMARY KEY REFERENCES person(id) ON DELETE CASCADE,
            hashed_password VARCHAR(255) NOT NULL,
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
            last_login_at TIMESTAMPTZ,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # ── department ────────────────────────────────────────────────────────────
    op.create_table(
        "department",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_department_name"),
    )

    # ── position ──────────────────────────────────────────────────────────────
    op.create_table(
        "position",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_position_name"),
    )

    # ── employee ──────────────────────────────────────────────────────────────
    op.create_table(
        "employee",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("employee_code", sa.String(30), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("position_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", postgresql.ENUM(name="employee_status", create_type=False), nullable=False, server_default="active"),
        sa.Column("hire_date", sa.Date, nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["id"], ["person.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["department.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["position_id"], ["position.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("employee_code", name="uq_employee_code"),
    )
    op.create_index("ix_employee_code", "employee", ["employee_code"])
    op.create_index("ix_employee_department_id", "employee", ["department_id"])
    op.create_index("ix_employee_position_id", "employee", ["position_id"])
    op.create_index("ix_employee_status", "employee", ["status"])

    # ── face_encoding ─────────────────────────────────────────────────────────
    op.create_table(
        "face_encoding",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", sa.Text, nullable=False),   # placeholder; vector se agrega abajo
        sa.Column("sample_index", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("model_name", sa.String(50), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employee.id"], ondelete="CASCADE"),
    )
    # Cambiar embedding a tipo vector(512) ahora que la extensión está activa
    op.execute("ALTER TABLE face_encoding ALTER COLUMN embedding TYPE vector(512) USING embedding::vector(512)")
    op.create_index("ix_face_encoding_employee_id", "face_encoding", ["employee_id"])
    # Índice IVFFlat para búsqueda por similitud coseno (eficiente con pgvector)
    op.execute("CREATE INDEX ix_face_encoding_embedding ON face_encoding USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")

    # ── attendance_log ────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE attendance_log (
            id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id  UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
            event_type   event_type NOT NULL,
            method       attendance_method NOT NULL DEFAULT 'face_recognition',
            event_time   TIMESTAMPTZ NOT NULL DEFAULT now(),
            confidence   FLOAT,
            snapshot_url VARCHAR(500),
            recorded_by  UUID REFERENCES "user"(id) ON DELETE SET NULL,
            notes        TEXT,
            created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.create_index("ix_attendance_log_employee_id", "attendance_log", ["employee_id"])
    op.create_index("ix_attendance_log_event_time", "attendance_log", ["event_time"])
    op.create_index("ix_attendance_log_event_type", "attendance_log", ["event_type"])

    # ── Trigger updated_at automático para todas las tablas ───────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    for table in ("person", '"user"', "department", "position", "employee", "face_encoding"):
        op.execute(f"""
            CREATE TRIGGER trg_{table.strip('"')}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
        """)


def downgrade() -> None:
    for table in ("person", "user", "department", "position", "employee", "face_encoding"):
        op.execute(f'DROP TRIGGER IF EXISTS trg_{table}_updated_at ON "{table}"')
    op.execute("DROP FUNCTION IF EXISTS update_updated_at()")

    op.drop_table("attendance_log")
    op.drop_table("face_encoding")
    op.drop_table("employee")
    op.drop_table("position")
    op.drop_table("department")
    op.execute('DROP TABLE IF EXISTS "user"')
    op.drop_table("person")

    op.execute("DROP TYPE IF EXISTS attendance_method")
    op.execute("DROP TYPE IF EXISTS event_type")
    op.execute("DROP TYPE IF EXISTS employee_status")
