# core/permissions.py (new file)
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff # or request.user.role == 'admin'

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj is the instance being accessed (e.g., a StudentProfile)
        if request.user and request.user.is_staff: # or request.user.role == 'admin'
            return True
        # Assumes the object has a 'user' attribute
        return obj.user == request.user

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'

class IsFaculty(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'faculty'

# core/views.py
# ...
from .permissions import IsAdminOrReadOnly, IsStudent, IsFaculty # etc.

class StudentProfileDetailView(generics.RetrieveUpdateDestroyAPIView): # Example
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin] # User can see/edit their own, admin can too

class ExamResultListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamResultSerializer
    # permission_classes = [permissions.IsAuthenticated] # Keep this as a base

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return ExamResult.objects.select_related('enrollment__student__user', 'exam__course', 'exam__exam_type').all()
        elif user.role == 'student':
            try:
                student_profile = user.studentprofile
                return ExamResult.objects.filter(enrollment__student=student_profile).select_related(...)
            except StudentProfile.DoesNotExist:
                return ExamResult.objects.none()
        elif user.role == 'faculty':
            try:
                faculty_profile = user.facultyprofile
                # Filter results for courses taught by this faculty, or students in their department etc.
                # This requires more complex logic, e.g., based on AttendanceSession.faculty or Course.faculty_assigned
                # For simplicity, let's assume faculty can see all for now, or restrict later
                return ExamResult.objects.filter(exam__course__department=faculty_profile.department).select_related(...) # Example
            except FacultyProfile.DoesNotExist:
                return ExamResult.objects.none()
        return ExamResult.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            # Only faculty (for courses they teach) or admin can create
            return [permissions.IsAuthenticated, IsFacultyOrAdminPermission()] # You'd create IsFacultyOrAdminPermission
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Add validation: ensure faculty is associated with the exam's course if they are creating
        serializer.save()