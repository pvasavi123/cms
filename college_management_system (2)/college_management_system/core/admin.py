# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Department, FacultyProfile, Semester, EventType, AcademicEvent, Notice, HelpRequest,
    StudentProfile, Course, Enrollment, ExamType, Exam, ExamResult,SportCategory, Sport, SportsTeam, SportsAchievement,
    AttendanceSession, StudentAttendance
)


# If using custom User model
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = BaseUserAdmin.list_display + ('role',)

admin.site.register(User, UserAdmin) # Use UserAdmin if custom User model
# If using default User, you might not need to re-register it unless extending admin view

admin.site.register(Department)
admin.site.register(FacultyProfile)
admin.site.register(Semester)
admin.site.register(EventType)
admin.site.register(AcademicEvent)
admin.site.register(Notice)
admin.site.register(HelpRequest)
admin.site.register(StudentProfile)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ExamType) # Register the new ExamType
admin.site.register(Exam)
admin.site.register(ExamResult)
admin.site.register(SportCategory)
admin.site.register(Sport)
admin.site.register(SportsTeam)
admin.site.register(SportsAchievement)
admin.site.register(AttendanceSession)
admin.site.register(StudentAttendance)

# ... (your other existing registrations) ...