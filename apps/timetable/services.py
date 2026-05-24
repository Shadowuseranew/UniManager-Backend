from datetime import date as date_type

import pyotp
from django.db import transaction

from apps.timetable.models import Attendance, Classroom, Lesson, TimeSlot

TOTP_INTERVAL = 3  # QR code changes every 3 seconds


class CollisionError(Exception):
    """Raised when a classroom or teacher is double-booked for a time slot."""

    pass


@transaction.atomic
def create_lesson(
    subject_id: int,
    group_id: int,
    classroom_id: int,
    time_slot_id: int,
    teacher_id: int,
    semester_id: int,
) -> Lesson:
    """Create a lesson with collision detection.

    Checks both classroom and teacher availability for the given time slot.
    Raises CollisionError if either is already booked.
    """
    classroom = Classroom.objects.get(id=classroom_id)
    time_slot = TimeSlot.objects.get(id=time_slot_id)

    if Lesson.objects.filter(time_slot=time_slot, classroom=classroom).exists():
        raise CollisionError(
            f'Classroom "{classroom.name}" is already booked for {time_slot}',
        )

    if Lesson.objects.filter(time_slot=time_slot, teacher_id=teacher_id).exists():
        raise CollisionError(
            'Teacher is already assigned to another lesson at this time',
        )

    return Lesson.objects.create(
        subject_id=subject_id,
        group_id=group_id,
        classroom=classroom,
        time_slot=time_slot,
        teacher_id=teacher_id,
        semester_id=semester_id,
    )


@transaction.atomic
def mark_attendance(
    lesson_id: int,
    student_id: int,
    status: str,
    date: date_type | None = None,
) -> Attendance:
    """Mark attendance for a single student in a lesson.

    Uses update_or_create so re-marking updates the existing record.
    """
    if date is None:
        date = date_type.today()
    attendance, _ = Attendance.objects.update_or_create(
        lesson_id=lesson_id,
        student_id=student_id,
        defaults={'status': status, 'date': date},
    )
    return attendance


@transaction.atomic
def bulk_mark_attendance(lesson_id: int, records: list[dict]) -> list[Attendance]:
    """Mark attendance for multiple students in one atomic transaction.

    Each record: {'student_id': int, 'status': str, 'date': str (optional)}.
    """
    attendances = []
    for record in records:
        att = mark_attendance(
            lesson_id=lesson_id,
            student_id=record['student_id'],
            status=record['status'],
            date=record.get('date'),
        )
        attendances.append(att)
    return attendances


def generate_lesson_qr_token(lesson_id: int) -> dict:
    """Generate a TOTP token for a lesson.

    Returns a dict with the current token and the secret used for verification.
    Token changes every TOTP_INTERVAL seconds.
    """
    totp = pyotp.TOTP(pyotp.random_base32(), interval=TOTP_INTERVAL)
    return {
        'token': totp.now(),
        'secret': totp.secret,
        'interval': TOTP_INTERVAL,
    }


def verify_qr_token(secret: str, token: str) -> bool:
    """Verify a TOTP token against the secret.

    Returns True if the token is valid within the time interval, False otherwise.
    """
    totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL)
    return totp.verify(token)
