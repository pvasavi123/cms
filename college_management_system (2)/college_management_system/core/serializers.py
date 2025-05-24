# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model # Use this to get the active User model
from .models import(
    AcademicEvent, EventType, Semester, FacultyProfile, Department, Notice, HelpRequest, User as CustomUserModel,
    StudentProfile, Course, Enrollment, ExamType, Exam, ExamResult,SportCategory, Sport, SportsTeam, SportsAchievement,
    AttendanceSession, StudentAttendance # Added new models
)

User = get_user_model() # Gets either default User or your custom User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User # Use the User model from get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role'] # Add 'role' if in your User model
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'student') # Set default role
        )
        return user

class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class AcademicEventSerializer(serializers.ModelSerializer):
    event_type = EventTypeSerializer(read_only=True)
    event_type_id = serializers.PrimaryKeyRelatedField(
        queryset=EventType.objects.all(), source='event_type', write_only=True
    )
    semester = serializers.StringRelatedField(read_only=True) # Display semester name
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), source='semester', write_only=True
    )

    class Meta:
        model = AcademicEvent
        fields = ['id', 'title', 'description', 'event_type', 'event_type_id',
                  'date_from', 'date_to', 'time', 'semester', 'semester_id']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class FacultyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Assuming UserSerializer is defined
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True, allow_null=True
    )
    # Basic user fields for creation/update, assuming user object is handled separately
    username = serializers.CharField(write_only=True, source='user.username', required=False)
    email = serializers.EmailField(write_only=True, source='user.email', required=False)


    class Meta:
        model = FacultyProfile
        fields = ['id', 'user', 'department', 'department_id', 'bio', 'profile_picture', 'username', 'email']


class NoticeSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'category', 'published_date', 'attachment', 'author_username']

class HelpRequestSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username', allow_null=True)
    class Meta:
        model = HelpRequest
        fields = ['id', 'user_username', 'subject', 'message', 'submitted_at', 'is_resolved']

# ... (your existing UserSerializer, EventTypeSerializer, SemesterSerializer, AcademicEventSerializer, etc.) ...

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Assuming UserSerializer is defined
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True, allow_null=True
    )

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'roll_number', 'date_of_birth', 'department_name', 'department_id', 'current_semester_number', 'profile_picture']

class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True
    )
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'course_name', 'description', 'credits', 'department_name', 'department_id']

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all(), source='student', write_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course', write_only=True)
    semester_id = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all(), source='semester', write_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student_name', 'student_id', 'course_name', 'course_id', 'semester_name', 'semester_id', 'enrollment_date', 'grade']

class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)

    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course', write_only=True)
    semester_id = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all(), source='semester', write_only=True)
    exam_type_id = serializers.PrimaryKeyRelatedField(queryset=ExamType.objects.all(), source='exam_type', write_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'course_name', 'course_id', 'semester_name', 'semester_id',
                  'exam_type_name', 'exam_type_id', 'exam_date', 'start_time', 'end_time', 'max_marks', 'venue']

class ExamResultSerializer(serializers.ModelSerializer):
    # You might want more details here depending on what the frontend needs
    student_name = serializers.CharField(source='enrollment.student.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='exam.course.course_name', read_only=True)
    exam_type = serializers.CharField(source='exam.exam_type.name', read_only=True)

    enrollment_id = serializers.PrimaryKeyRelatedField(queryset=Enrollment.objects.all(), source='enrollment', write_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all(), source='exam', write_only=True)


    class Meta:
        model = ExamResult
        fields = ['id', 'student_name', 'course_name', 'exam_type', 'marks_obtained', 'enrollment_id', 'exam_id']         


class SportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SportCategory
        fields = ['id', 'name', 'description', 'icon_class']

class SportSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=SportCategory.objects.all(), source='category', write_only=True
    )
    coach_name = serializers.CharField(source='coach.user.get_full_name', read_only=True, allow_null=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=FacultyProfile.objects.all(), source='coach', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Sport
        fields = ['id', 'name', 'description', 'category_name', 'category_id', 'coach_name', 'coach_id']

class SportsTeamSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    sport_id = serializers.PrimaryKeyRelatedField(
        queryset=Sport.objects.all(), source='sport', write_only=True
    )
    captain_name = serializers.CharField(source='captain.user.get_full_name', read_only=True, allow_null=True)
    captain_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), source='captain', write_only=True, allow_null=True, required=False
    )
    # For ManyToManyField, PrimaryKeyRelatedField is often used for writing
    members_ids = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), source='members', write_only=True, many=True, required=False
    )
    # For reading members, you might want a nested serializer or just IDs
    members = StudentProfileSerializer(many=True, read_only=True) # Example of nested for reading

    class Meta:
        model = SportsTeam
        fields = ['id', 'name', 'sport_name', 'sport_id', 'captain_name', 'captain_id', 'season_year', 'members', 'members_ids']

class SportsAchievementSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True, allow_null=True)
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=SportsTeam.objects.all(), source='team', write_only=True, allow_null=True, required=False
    )
    student_name = serializers.CharField(source='individual_student.user.get_full_name', read_only=True, allow_null=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), source='individual_student', write_only=True, allow_null=True, required=False
    )
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    sport_id = serializers.PrimaryKeyRelatedField(
        queryset=Sport.objects.all(), source='sport', write_only=True
    )

    class Meta:
        model = SportsAchievement
        fields = [
            'id', 'achievement_details', 'date_achieved', 'competition_name',
            'team_name', 'team_id', 'student_name', 'student_id', 'sport_name', 'sport_id'
        ]


# --- Attendance Serializers ---

class AttendanceSessionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), source='semester', write_only=True
    )
    faculty_name = serializers.CharField(source='faculty.user.get_full_name', read_only=True, allow_null=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=FacultyProfile.objects.all(), source='faculty', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'session_date', 'start_time', 'end_time', 'topic_covered',
            'course_name', 'course_id', 'semester_name', 'semester_id', 'faculty_name', 'faculty_id'
        ]

class StudentAttendanceSerializer(serializers.ModelSerializer):
    session_details = AttendanceSessionSerializer(source='session', read_only=True) # Read-only nested details
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=AttendanceSession.objects.all(), source='session', write_only=True
    )
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentProfile.objects.all(), source='student', write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True) # Human-readable status

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'status', 'status_display', 'marked_at', 'reason_if_absent',
            'session_details', 'session_id', 'student_name', 'student_roll_number', 'student_id'
        ]
# core/serializers.py
class FacultyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # For reading
    user_id = serializers.IntegerField(write_only=True, required=False) # To link to existing user

    # Fields to create a NEW user if user_id is not provided
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    # ... other user fields

    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True, allow_null=True
    )

    class Meta:
        model = FacultyProfile
        fields = [
            'id', 'user', 'user_id', 'username', 'email', 'password', # etc.
            'department', 'department_id', 'bio', 'profile_picture'
        ]

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username', None),
            'email': validated_data.pop('email', None),
            'password': validated_data.pop('password', None),
            'role': 'faculty' # Explicitly set role
        }
        # Filter out None values for user_data
        user_data = {k: v for k, v in user_data.items() if v is not None}

        user_id = validated_data.pop('user_id', None)
        user = None

        if user_id:
            user = User.objects.get(id=user_id, role='faculty') # Ensure it's a faculty user
        elif user_data.get('username') and user_data.get('password'):
            user = User.objects.create_user(**user_data)
        else:
            raise serializers.ValidationError("Either user_id or username/password must be provided for faculty.")

        faculty_profile = FacultyProfile.objects.create(user=user, **validated_data)
        return faculty_profile

    # You'd need a similar `update` method if you want to update user details via this serializer
# To handle bulk attendance marking for a session:
#cass BulkStudentAttendanceSerializer(serializers.ListSerializer):
 #  child = StudentAttendanceSerializer()

 #  def create(self, validated_data):
   #    attendances = [StudentAttendance(**item) for item in validated_data]
   #    return StudentAttendance.objects.bulk_create(attendances)

    # You might need an update method too if you allow bulk updates        