# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# If you want to add roles directly to the User model:
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    # Add any other common fields here

    # To avoid clash with default User model if you named your app 'auth' or similar
    # class Meta:
    #     db_table = 'auth_user_custom'


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class FacultyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='faculty_pics/', blank=True, null=True)
    # Add other faculty-specific fields: rating, courses, etc.

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Semester(models.Model):
    name = models.CharField(max_length=50) # e.g., "Semester 1 (August - December 2024)"
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class EventType(models.Model):
    name = models.CharField(max_length=50, unique=True) # Academic, Exam, Holiday, Event
    color_class = models.CharField(max_length=50, blank=True) # e.g., 'academic', 'exam' for CSS

    def __str__(self):
        return self.name

class AcademicEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField(null=True, blank=True) # For multi-day events
    time = models.TimeField(null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return self.title

class Notice(models.Model):
    CATEGORY_CHOICES = (
        ('urgent', 'Urgent'),
        ('academic', 'Academic'),
        ('event', 'Event'),
        ('general', 'General'),
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    published_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='notice_attachments/', blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class HelpRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True) # Can be anonymous
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

# ... Add other models: Course, StudentProfile, Attendance, Exam, Club, Fee, etc.
# core/models.py

# ... (your existing User, Department, FacultyProfile, Semester, EventType, AcademicEvent, Notice, HelpRequest models) ...

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    roll_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    current_semester_number = models.PositiveIntegerField(null=True, blank=True) # e.g., 1, 2, 3...
    profile_picture = models.ImageField(upload_to='student_pics/', blank=True, null=True)
    # Add other student-specific fields: address, phone_number, parent_info etc.

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    # You could link this to specific semesters or faculty if needed
    # faculty_assigned = models.ManyToManyField(FacultyProfile, blank=True, related_name='courses_taught')

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=5, blank=True, null=True) # e.g., A+, B, Pass

    class Meta:
        unique_together = ('student', 'course', 'semester') # A student can enroll in a course only once per semester

    def __str__(self):
        return f"{self.student} enrolled in {self.course} for {self.semester}"

class ExamType(models.Model): # Renaming your existing EventType to be more specific or keep it general
    name = models.CharField(max_length=50, unique=True) # Internal, External, Midterm, Semester Final
    # If you want to reuse your existing EventType and add a filter, that's also an option.
    # For clarity, I'm making a new one here specifically for exams.
    # If you reuse EventType, make sure your front-end knows how to filter.

    def __str__(self):
        return self.name

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE) # Link to the new ExamType or your existing EventType
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_marks = models.PositiveIntegerField(default=100)
    venue = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.exam_type} for {self.course} on {self.exam_date}"

class ExamResult(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='exam_results_for_enrollment') # Clarified related_name
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.PositiveIntegerField()
    # feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('enrollment', 'exam') # A student has one result per exam for a given enrollment

    def __str__(self):
        return f"Result for {self.enrollment.student} in {self.exam.course} ({self.exam.exam_type})"


# You can continue adding more models for Clubs, Sports, Fee Payments, Attendance etc.
# For example:
class Club(models.Model):
      name = models.CharField(max_length=100, unique=True)
      description = models.TextField()
      category = models.CharField(max_length=50) # sports, arts, technical, etc.
      faculty_advisor = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True)
      members = models.ManyToManyField(StudentProfile, blank=True, related_name='clubs_joined')
class FeeStructure(models.Model):
     fee_type = models.CharField(max_length=100) # Tuition, Hostel, Mess
     amount = models.DecimalField(max_digits=10, decimal_places=2)
     semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
     category = models.CharField(max_length=20, default='regular') # Regular, Govt Employee Parent

class FeePayment(models.Model):
     student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
     fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
     amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
     payment_date = models.DateField(auto_now_add=True)
     transaction_id = models.CharField(max_length=100, unique=True)
     payment_proof = models.FileField(upload_to='payment_proofs/')
     is_verified = models.BooleanField(default=False)

# ... (your existing User, Department, FacultyProfile, Semester, EventType, AcademicEvent,
#       Notice, HelpRequest, StudentProfile, Course, Enrollment, ExamType, Exam, ExamResult models) ...


# --- Sports Models ---

class SportCategory(models.Model):
    """
    To categorize sports, e.g., Team Sports, Athletics, Indoor Sports.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True) # e.g., 'fas fa-futbol' for FontAwesome

    def __str__(self):
        return self.name

class Sport(models.Model):
    """
    Represents an individual sport.
    """
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(SportCategory, on_delete=models.CASCADE, related_name='sports')
    description = models.TextField(blank=True, null=True)
    coach = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='coached_sports', limit_choices_to={'role': 'faculty'}) # Assuming coaches can be faculty
    # You could also have a separate Coach model if coaches are not always faculty.

    def __str__(self):
        return self.name

class SportsTeam(models.Model):
    """
    Represents a specific team for a sport, possibly for a specific year/season.
    """
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100) # e.g., "Cricket Senior Team 2024", "Chess Club Team A"
    captain = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='captained_teams')
    members = models.ManyToManyField(StudentProfile, blank=True, related_name='sports_teams')
    season_year = models.PositiveIntegerField(null=True, blank=True) # e.g., 2024

    class Meta:
        unique_together = ('sport', 'name', 'season_year') # Ensure team names are unique within a sport for a season

    def __str__(self):
        return f"{self.name} ({self.sport.name})"

class SportsAchievement(models.Model):
    """
    To record achievements of teams or individuals.
    """
    team = models.ForeignKey(SportsTeam, on_delete=models.CASCADE, null=True, blank=True, related_name='achievements')
    individual_student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='sports_achievements')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE) # To link achievement even if not team-specific
    achievement_details = models.CharField(max_length=255) # e.g., "State Champions 2023", "Gold Medal - 100m Sprint"
    date_achieved = models.DateField()
    competition_name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        if self.team:
            return f"{self.team.name} - {self.achievement_details}"
        elif self.individual_student:
            return f"{self.individual_student.user.get_full_name()} - {self.achievement_details}"
        return f"{self.sport.name} - {self.achievement_details}"


# --- Attendance Models ---

class AttendanceSession(models.Model):
    """
    Represents a single class session for which attendance is taken.
    This could be linked to a timetable system if you build one.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.SET_NULL, null=True) # Faculty who took the class
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    topic_covered = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # A course session is unique for a given date and start time
        unique_together = ('course', 'session_date', 'start_time')

    def __str__(self):
        return f"{self.course.course_name} on {self.session_date} at {self.start_time} by {self.faculty}"

class StudentAttendance(models.Model):
    """
    Records the attendance status of a specific student for a specific session.
    """
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused Absence'),
    )
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='student_attendances')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_at = models.DateTimeField(auto_now_add=True) # When this record was created/updated
    reason_if_absent = models.TextField(blank=True, null=True) # For excused absences or specific reasons

    class Meta:
        # A student can only have one attendance record per session
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.session.course.course_name} ({self.session.session_date}) - {self.get_status_display()}"