from django.db import transaction
from django.contrib.auth import get_user_model

from apps.academic.models import (
    AcademicYear,
    Department,
    Enrollment,
    Faculty,
    Group,
    Semester,
    Subject,
)

User = get_user_model()


@transaction.atomic
def create_academic_structure(
    faculty_name: str,
    faculty_slug: str,
    department_name: str,
    subject_name: str,
    subject_code: str,
    year_name: str,
    semester_number: int,
    semester_start: str,
    semester_end: str,
    group_name: str,
    year_of_study: int = 1,
) -> dict:
    """Create a complete academic hierarchy in a single atomic transaction.

    Creates or fetches: Faculty → Department → Subject → AcademicYear → Semester → Group.
    Returns a dict with all created/retrieved objects.
    """
    faculty, _ = Faculty.objects.get_or_create(name=faculty_name, slug=faculty_slug)
    department, _ = Department.objects.get_or_create(
        name=department_name, faculty=faculty,
    )
    subject, _ = Subject.objects.get_or_create(
        name=subject_name, code=subject_code, department=department,
    )
    academic_year, _ = AcademicYear.objects.get_or_create(name=year_name)
    semester, _ = Semester.objects.get_or_create(
        academic_year=academic_year,
        number=semester_number,
        defaults={'start_date': semester_start, 'end_date': semester_end},
    )
    group, _ = Group.objects.get_or_create(
        name=group_name,
        department=department,
        semester=semester,
        year_of_study=year_of_study,
    )
    return {
        'faculty': faculty,
        'department': department,
        'subject': subject,
        'academic_year': academic_year,
        'semester': semester,
        'group': group,
    }


def create_semester_group(
    name: str,
    department_id: int,
    semester_id: int,
    year_of_study: int = 1,
) -> Group:
    """Create a single Group linked to a Department and Semester."""
    department = Department.objects.get(id=department_id)
    semester = Semester.objects.get(id=semester_id)
    return Group.objects.create(
        name=name,
        department=department,
        semester=semester,
        year_of_study=year_of_study,
    )


@transaction.atomic
def enroll_student(student_id: int, group_id: int, semester_id: int) -> Enrollment:
    """Enroll a student in a group for a given semester.

    Uses get_or_create so repeated calls are idempotent.
    """
    student = User.objects.get(id=student_id, role='student')
    group = Group.objects.get(id=group_id)
    semester = Semester.objects.get(id=semester_id)
    enrollment, _ = Enrollment.objects.get_or_create(
        student=student, group=group, semester=semester,
    )
    return enrollment
