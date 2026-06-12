"""Add schedule table

Revision ID: 002
Revises: 001
Create Date: 2026-05-29

Diseño normalizado (1FN – 3FN):
  · Cada columna es atómica y depende únicamente de la PK (id UUID).
  · No existen dependencias parciales ni transitivas.
  · timezone, check_in_start, etc. son atributos directos del schedule.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schedule",
        # ── Clave primaria ────────────────────────────────────────────────────
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        # ── Identificación ────────────────────────────────────────────────────
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # ── Zona horaria del nodo que ejecuta camera_client ───────────────────
        # Almacenado como cadena IANA (ej. "America/Bogota").
        # Permite que distintas instalaciones corran en husos diferentes.
        sa.Column(
            "timezone",
            sa.String(60),
            nullable=False,
            server_default="America/Bogota",
        ),
        # ── Ventana check-in ──────────────────────────────────────────────────
        sa.Column("check_in_start", sa.Time(timezone=False), nullable=False),
        sa.Column("check_in_end",   sa.Time(timezone=False), nullable=False),
        # ── Ventana check-out ─────────────────────────────────────────────────
        sa.Column("checkout_start", sa.Time(timezone=False), nullable=False),
        sa.Column("checkout_end",   sa.Time(timezone=False), nullable=False),
        # ── Estado ────────────────────────────────────────────────────────────
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="false"),
        # ── Auditoría ─────────────────────────────────────────────────────────
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # ── Restricciones ─────────────────────────────────────────────────────
        sa.UniqueConstraint("name", name="uq_schedule_name"),
    )

    # Índice para la consulta más frecuente: obtener el horario activo.
    op.create_index("ix_schedule_is_active", "schedule", ["is_active"])

    # ── Horario por defecto (Colombia) ────────────────────────────────────────
    # Se inserta listo para usar. El administrador puede editarlo o crear uno nuevo.
    op.execute("""
        INSERT INTO schedule (
            id, name, description, timezone,
            check_in_start, check_in_end,
            checkout_start, checkout_end,
            is_active
        ) VALUES (
            gen_random_uuid(),
            'Jornada Colombia',
            'Horario por defecto para instalaciones en Colombia. '
            'Entrada: 08:00–12:00 | Salida: 13:00–23:59. '
            'Modifique según las necesidades de su organización.',
            'America/Bogota',
            '08:00:00', '12:00:00',
            '13:00:00', '23:59:59',
            true
        )
    """)


def downgrade() -> None:
    op.drop_index("ix_schedule_is_active", table_name="schedule")
    op.drop_table("schedule")
