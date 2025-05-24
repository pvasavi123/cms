from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.generic import TemplateView
from django.shortcuts import render

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