from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'

    def __str__(self) -> str:
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name='departments',
    )

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self) -> str:
        return f'{self.name} ({self.faculty.name})'


class Subject(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='subjects',
    )

    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self) -> str:
        return f'{self.code} - {self.name}'


class AcademicYear(models.Model):
    name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'

    def __str__(self) -> str:
        return self.name


class Semester(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name='semesters',
    )
    number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'

    def __str__(self) -> str:
        return f'Semester {self.number} ({self.academic_year.name})'


class Group(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='groups',
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='groups',
    )
    year_of_study = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self) -> str:
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='enrollments',
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ['student', 'group', 'semester']

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.student.email} -> {self.group.name}'
