# core/urls.py
from django.urls import path
from . import views

# For serving individual HTML files (if not building an SPA)
html_patterns = [
    path('', views.IndexView.as_view(), name='index-html'), # Serves index.html for root
    path('<str:page_name>', views.serve_html, name='serve-html'),
]


urlpatterns = [
    # Auth
      path('api/student/today-schedule/', views.StudentTodayScheduleView.as_view(), name='student-today-schedule'),
      path('api/student/attendance-summary/', views.StudentAttendanceSummaryView.as_view(), name='student-attendance-summary'),
    # ... other urls
    path('api/auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='logout'),

    # API Endpoints
    path('api/academic-events/', views.AcademicEventListCreateView.as_view(), name='academic-event-list-create'),
    path('api/semesters/', views.SemesterListView.as_view(), name='semester-list'),
    path('api/faculty/', views.FacultyProfileListView.as_view(), name='faculty-list'),
    path('api/notices/', views.NoticeListView.as_view(), name='notice-list'),
    path('api/help-requests/', views.HelpRequestCreateView.as_view(), name='help-request-create'),
    path('api/student-profiles/', views.StudentProfileListCreateView.as_view(), name='studentprofile-list-create'),
    path('api/courses/', views.CourseListCreateView.as_view(), name='course-list-create'),
    path('api/enrollments/', views.EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('api/exam-types/', views.ExamTypeListCreateView.as_view(), name='examtype-list-create'),
    path('api/exams/', views.ExamListCreateView.as_view(), name='exam-list-create'),
    path('api/exam-results/', views.ExamResultListCreateView.as_view(), name='examresult-list-create'),
    
    # Sports URLs
    path('api/sport-categories/', views.SportCategoryListCreateView.as_view(), name='sportcategory-list-create'),
    path('api/sports/', views.SportListCreateView.as_view(), name='sport-list-create'),
    path('api/sports-teams/', views.SportsTeamListCreateView.as_view(), name='sportsteam-list-create'),
    path('api/sports-achievements/', views.SportsAchievementListCreateView.as_view(), name='sportsachievement-list-create'),

    # Attendance URLs
    path('api/attendance-sessions/', views.AttendanceSessionListCreateView.as_view(), name='attendancesession-list-create'),
    path('api/student-attendances/', views.StudentAttendanceListCreateView.as_view(), name='studentattendance-list-create'),
    # If using bulk attendance:
    #ath('api/mark-bulk-attendance/', views.MarkBulkAttendanceView.as_view(), name='mark-bulk-attendance'),

path('api/student/attendance-summary/', views.StudentAttendanceSummaryView.as_view(), name='student-attendance-summary'),
path('api/student/today-schedule/', views.StudentTodayScheduleView.as_view(), name='student-today-schedule'),
path('api/dashboard/', views.DashboardDataView.as_view(), name='dashboard-data'),

    # Add other API endpoints here...
] + html_patterns # Add HTML serving patterns AFTER API patterns