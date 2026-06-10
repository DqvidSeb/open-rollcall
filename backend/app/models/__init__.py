"""
Exporta todos los modelos para que Alembic los detecte automáticamente.
El orden de importación respeta las dependencias FK.
"""

from app.models.base import Base
from app.models.person import Person
from app.models.user import User
from app.models.department import Department
from app.models.position import Position
from app.models.employee import Employee, EmployeeStatus
from app.models.academic_program import AcademicProgram
from app.models.student import Student, StudentStatus
from app.models.face_encoding import FaceEncoding
from app.models.attendance_log import AttendanceLog, EventType, AttendanceMethod
from app.models.schedule import Schedule

__all__ = [
    "Base",
    "Person",
    "User",
    "Department",
    "Position",
    "Employee",
    "EmployeeStatus",
    "AcademicProgram",
    "Student",
    "StudentStatus",
    "FaceEncoding",
    "AttendanceLog",
    "EventType",
    "AttendanceMethod",
    "Schedule",
]
