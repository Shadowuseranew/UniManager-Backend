from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from apps.academic.models import (
    AcademicYear,
    Department,
    Enrollment,
    Faculty,
    Group,
    Semester,
    Subject,
)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')
    list_filter = ('faculty',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department')
    list_filter = ('department__faculty', 'department')
    search_fields = ('code', 'name')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number', 'academic_year', 'start_date', 'end_date')
    list_filter = ('academic_year',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'semester', 'year_of_study')
    list_filter = ('department__faculty', 'semester__academic_year', 'year_of_study')


@admin.register(Enrollment)
class EnrollmentAdmin(SimpleHistoryAdmin):
    list_display = ('student', 'group', 'semester', 'enrolled_at')
    list_filter = ('semester__academic_year', 'group')
    search_fields = ('student__email', 'group__name')
