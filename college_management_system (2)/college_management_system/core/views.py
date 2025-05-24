from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.generic import TemplateView
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from django.db.models import Count, F # You might need these for aggregation


from .models import ( 
            AcademicEvent, FacultyProfile, Notice, HelpRequest, Semester,StudentProfile, Course, 
            Enrollment, ExamType, Exam, ExamResult,SportCategory, Sport, SportsTeam, SportsAchievement,
             AttendanceSession, StudentAttendance
)             
from .serializers import (
    UserSerializer, AcademicEventSerializer, FacultyProfileSerializer,
    NoticeSerializer, HelpRequestSerializer, SemesterSerializer,StudentProfileSerializer,
    CourseSerializer, EnrollmentSerializer, ExamTypeSerializer, ExamSerializer, ExamResultSerializer,
    SportCategorySerializer, SportSerializer, SportsTeamSerializer, SportsAchievementSerializer,
    AttendanceSessionSerializer, StudentAttendanceSerializer
)

User = get_user_model()

# --- Authentication Views ---
class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
# Add this class definition to your core/views.py file

class StudentTodayScheduleView(APIView):
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request, *args, **kwargs):
            user = request.user
            try:
                student_profile = user.studentprofile # Assuming the one-to-one relationship
            except StudentProfile.DoesNotExist:
                return Response({'error': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)

            today = timezone.now().date()
            # Get the current day of the week as a number (0 for Monday, 6 for Sunday)
            today_weekday = today.weekday()

            # Find the current semester (assuming you have a way to mark the current semester)
            try:
                current_semester = Semester.objects.get(is_current=True) # Example
            except Semester.DoesNotExist:
                # If no current semester is defined, there's no schedule for the current semester
                return Response([], status=status.HTTP_200_OK)


            # Get the courses the student is enrolled in for the current semester
            # Ensure 'enrollments' is the correct related_name or accessor on StudentProfile
            enrolled_course_ids = student_profile.enrollments.filter(
                semester=current_semester
            ).values_list('course', flat=True)


            # Find schedule entries for these courses for today's weekday
            # This assumes you have a Schedule model linked to Course and storing weekday and time.
            # You will need to adapt this query based on your actual scheduling models.
            # Example query structure (might need significant adjustment based on your models):
            # Make sure you have a Schedule model imported and linked to Course
            from .models import Schedule # Import Schedule model if you have one

            today_schedule_entries = Schedule.objects.filter(
                course__id__in=enrolled_course_ids,
                day_of_week=today_weekday, # Assuming a field to store weekday number (0-6)
                semester=current_semester # Filter by the current semester
            ).order_by('start_time') # Assuming a field for start time


            # Serialize the schedule entries
            # You will need a serializer for your Schedule model, e.g., ScheduleSerializer
            # from .serializers import ScheduleSerializer
            # serializer = ScheduleSerializer(today_schedule_entries, many=True)

            # For now, let's return a simplified dictionary list if you don't have a ScheduleSerializer ready
            simplified_schedule_data = []
            for entry in today_schedule_entries:
                simplified_schedule_data.append({
                    'course_name': entry.course.course_name, # Example field name - adjust
                    'start_time': entry.start_time.strftime('%H:%M'), # Example formatting - adjust field name
                    'end_time': entry.end_time.strftime('%H:%M'), # Example formatting - adjust field name
                    'location': entry.location # Example field name - adjust
                    # Add other fields as needed to match your Schedule model and what the frontend expects
                })


            # return Response(serializer.data, status=status.HTTP_200_OK) # Use this if you have a serializer
            return Response(simplified_schedule_data, status=status.HTTP_200_OK) # Use this with simplified data

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user) # For session auth if used by browsable API
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({'token': token.key, 'user': user_data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            # Delete the token
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass # User might not have a token or already logged out
        logout(request) # For session auth
        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


# --- API List/Create Views ---
class AcademicEventListCreateView(generics.ListCreateAPIView):
    queryset = AcademicEvent.objects.select_related('event_type', 'semester').all().order_by('date_from', 'time')
    serializer_class = AcademicEventSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Adjust as needed

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()] # Only admins can create
        return [permissions.AllowAny()] # Anyone can read
class StudentAttendanceSummaryView(APIView):
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request, *args, **kwargs):
            user = request.user
            try:
                student_profile = user.studentprofile # Assuming the one-to-one relationship accessor is 'studentprofile'
            except StudentProfile.DoesNotExist:
                return Response({'error': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Calculate total sessions for the student's enrolled courses in the current semester (complex logic)
            # This is a simplified calculation. A real-world scenario might involve:
            # 1. Getting the student's enrollments for the current semester.
            # 2. Getting the courses from those enrollments.
            # 3. Getting all attendance sessions for those courses in that semester.
            # For simplicity here, let's count all attendance sessions the student *could* have attended based on enrollments.

            # A more robust approach would involve filtering AttendanceSession based on courses from Enrollments
            # Here's a simplified approach counting all sessions related to courses the student is enrolled in
            enrolled_course_ids = student_profile.enrollments.filter(
                semester__is_current=True # Assuming you have an 'is_current' flag on Semester
            ).values_list('course__id', flat=True)

            total_sessions = AttendanceSession.objects.filter(
                course__id__in=enrolled_course_ids,
                semester__is_current=True # Filter by current semester if needed
            ).count()


            # Calculate attended sessions for the student
            attended_sessions = StudentAttendance.objects.filter(
                student=student_profile,
                session__semester__is_current=True, # Filter by current semester
                is_present=True
            ).count()

            attendance_percentage = 0
            if total_sessions > 0:
                attendance_percentage = (attended_sessions / total_sessions) * 100

            return Response({
                'attendance_percentage': round(attendance_percentage, 2),
                'attended_sessions': attended_sessions,
                'total_sessions': total_sessions,
            }, status=status.HTTP_200_OK)

class SemesterListView(generics.ListAPIView):
    queryset = Semester.objects.all().order_by('start_date')
    serializer_class = SemesterSerializer
    permission_classes = [permissions.AllowAny]


class FacultyProfileListView(generics.ListAPIView):
    queryset = FacultyProfile.objects.select_related('user', 'department').all()
    serializer_class = FacultyProfileSerializer
    permission_classes = [permissions.AllowAny] # Or IsAuthenticatedOrReadOnly

class NoticeListView(generics.ListAPIView):
    queryset = Notice.objects.select_related('author').all().order_by('-published_date')
    serializer_class = NoticeSerializer
    permission_classes = [permissions.AllowAny]

class HelpRequestCreateView(generics.CreateAPIView):
    queryset = HelpRequest.objects.all()
    serializer_class = HelpRequestSerializer
    permission_classes = [permissions.AllowAny] # Or IsAuthenticated for logged-in users

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save() # Anonymous submission


# --- Views to serve your HTML files (Example) ---
# This approach is for a Multi-Page Application (MPA) feel.
# If you are building a Single Page Application (SPA) with React/Vue/Angular,
# you'd typically serve only one index.html and let the frontend handle routing.

class IndexView(TemplateView):
    template_name = "index.html" # Assumes index.html is in frontend_build/

def serve_html(request, page_name):
    """Serves various HTML pages dynamically."""
    # Ensure page_name is safe to prevent directory traversal
    safe_page_names = [
        "academic.html", "attendence.html", "club.html", "dash.html",
        "exam.html", "faculty.html", "fee.html", "index.html",
        "login.html", "logout.html", "notice.html", "scedule.html",
         "signup.html", "sports.html"
    ]
    if page_name in safe_page_names:
        return render(request, page_name)
    else:
        # Optionally, render a 404 page or redirect
        return render(request, "index.html") # Fallback to index or 404
class StudentProfileListCreateView(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.select_related('user', 'department').all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can list/create student profiles directly usually

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.select_related('department').all()
    serializer_class = CourseSerializer
    def get_permissions(self): # Allow anyone to read, but only admin to create/edit
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.select_related('student__user', 'course', 'semester').all()
    serializer_class = EnrollmentSerializer
    # Permissions might be: students can see their own, faculty can see their courses, admin can see all
    # For now, let's make it admin-only for create, read for authenticated
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()] # Or faculty for enrollments
        return [permissions.IsAuthenticated()]

class ExamTypeListCreateView(generics.ListCreateAPIView):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [permissions.IsAdminUser] # Usually managed by admin

class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.select_related('course', 'semester', 'exam_type').all()
    serializer_class = ExamSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()] # Or faculty for their courses
        return [permissions.AllowAny()] # Allow anyone to see exam schedule

class ExamResultListCreateView(generics.ListCreateAPIView):
    queryset = ExamResult.objects.select_related('enrollment__student__user', 'exam__course', 'exam__exam_type').all()
    serializer_class = ExamResultSerializer
    # Permissions: Students see their own, faculty their courses, admin all
    def get_permissions(self):
        if self.request.method == 'POST': # Faculty/Admin can post results
            return [permissions.IsAuthenticated] # More specific: IsFacultyOrAdmin
        return [permissions.IsAuthenticated] # Students can view (filtered later)  
class SportCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SportCategory.objects.all()
    serializer_class = SportCategorySerializer
    permission_classes = [permissions.IsAdminUser] # Typically managed by admin

class SportListCreateView(generics.ListCreateAPIView):
    queryset = Sport.objects.select_related('category', 'coach__user').all()
    serializer_class = SportSerializer
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()] # Or sports admin/faculty
        return [permissions.AllowAny()]

class SportsTeamListCreateView(generics.ListCreateAPIView):
    queryset = SportsTeam.objects.select_related('sport', 'captain__user').prefetch_related('members__user').all()
    serializer_class = SportsTeamSerializer
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()] # Or sports admin/coach
        return [permissions.IsAuthenticated()] # Logged-in users can view

class SportsAchievementListCreateView(generics.ListCreateAPIView):
    queryset = SportsAchievement.objects.select_related('team', 'individual_student__user', 'sport').all()
    serializer_class = SportsAchievementSerializer
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()] # Or sports admin
        return [permissions.AllowAny()]


# --- Attendance Views ---

class AttendanceSessionListCreateView(generics.ListCreateAPIView):
    queryset = AttendanceSession.objects.select_related('course', 'semester', 'faculty__user').all()
    serializer_class = AttendanceSessionSerializer
    def get_permissions(self): # Faculty can create sessions for their courses, Admin can do all
        if self.request.method == 'POST':
            # Implement more specific: IsFacultyAndOwnsCourseOrAdmin
            return [permissions.IsAuthenticated] # Placeholder, refine this
        return [permissions.IsAuthenticated] # Students might view sessions relevant to them

class StudentAttendanceListCreateView(generics.ListCreateAPIView):
    queryset = StudentAttendance.objects.select_related('session__course', 'student__user').all()
    serializer_class = StudentAttendanceSerializer
    # For marking attendance (POST), usually by faculty.
    # For viewing (GET), students see their own, faculty their sessions.
    def get_permissions(self):
        if self.request.method == 'POST':
            # Implement more specific: IsFacultyForSessionOrAdmin
            return [permissions.IsAuthenticated] # Placeholder
        return [permissions.IsAuthenticated]

    # Example: If you wanted to allow fetching attendance for a specific session
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     session_id = self.request.query_params.get('session_id')
    #     if session_id:
    #         queryset = queryset.filter(session_id=session_id)
    #     # Further filter by request.user if student/faculty
    #     return queryset

# If you use BulkStudentAttendanceSerializer for POSTing multiple records:
# class MarkBulkAttendanceView(generics.CreateAPIView):
#     serializer_class = BulkStudentAttendanceSerializer
#     permission_classes = [permissions.IsAuthenticated] # Refine: IsFacultyForSessionOrAdmin
#
#     def create(self, request, *args, **kwargs):
#         # Assuming request.data is a list of attendance records for a single session
#         # You might pass session_id in the URL or in each item in the list
#         serializer = self.get_serializer(data=request.data, many=True)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)