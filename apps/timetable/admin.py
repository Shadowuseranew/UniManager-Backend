from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from apps.timetable.models import Attendance, Classroom, Lesson, TimeSlot


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)


@admin.register(Lesson)
class LessonAdmin(SimpleHistoryAdmin):
    list_display = ('subject', 'group', 'teacher', 'classroom', 'time_slot', 'semester')
    list_filter = ('semester', 'time_slot__day_of_week')
    search_fields = ('subject__name', 'group__name', 'teacher__email')


@admin.register(Attendance)
class AttendanceAdmin(SimpleHistoryAdmin):
    list_display = ('student', 'lesson', 'status', 'date')
    list_filter = ('status', 'date', 'lesson__semester')
    search_fields = ('student__email',)
