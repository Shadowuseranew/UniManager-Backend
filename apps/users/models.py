from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class UserRole(models.TextChoices):
    STUDENT = 'student', 'Student'
    TEACHER = 'teacher', 'Teacher'
    ADMIN = 'admin', 'Admin'
    SUPERADMIN = 'superadmin', 'Superadmin'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.email} - {self.get_role_display()}'
