from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Assessment, Attendance, ClassGroup, Enrollment, Grade, Notification, Student, Subject, Teacher, Term
from .permissions import AcademicReadWritePermission
from .services import enroll_student
from .serializers import (
    AssessmentSerializer, AttendanceSerializer, ClassGroupSerializer, EnrollmentSerializer,
    GradeSerializer, NotificationSerializer, StudentSerializer, SubjectSerializer,
    TeacherSerializer, TermSerializer,
)


class ScopedSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, AcademicReadWritePermission]


class StudentViewSet(ScopedSet):
    serializer_class = StudentSerializer
    search_fields = ["student_number", "user__first_name", "user__last_name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()
        user = self.request.user
        queryset = Student.objects.select_related("user")
        if user.role == "student":
            return queryset.filter(user=user)
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(enrollments__class_group__assignments__teacher=user.teacher_profile).distinct()
        if user.role == "coordinator" or user.is_superuser:
            return queryset
        return queryset.none()


class TeacherViewSet(ScopedSet):
    queryset = Teacher.objects.select_related("user")
    serializer_class = TeacherSerializer
    search_fields = ["employee_number", "user__first_name", "user__last_name"]


class SubjectViewSet(ScopedSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ["code", "name"]


class TermViewSet(ScopedSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class ClassGroupViewSet(ScopedSet):
    serializer_class = ClassGroupSerializer
    search_fields = ["code", "term__name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ClassGroup.objects.none()
        user = self.request.user
        queryset = ClassGroup.objects.select_related("term")
        if user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(enrollments__student=user.student_profile)
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(assignments__teacher=user.teacher_profile, assignments__active=True).distinct()
        if user.role == "coordinator" or user.is_superuser:
            return queryset
        return queryset.none()


class EnrollmentViewSet(ScopedSet):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Enrollment.objects.none()
        user = self.request.user
        queryset = Enrollment.objects.select_related("student__user", "class_group")
        if user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(student=user.student_profile)
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(class_group__assignments__teacher=user.teacher_profile, class_group__assignments__active=True).distinct()
        if user.role == "coordinator" or user.is_superuser:
            return queryset
        return queryset.none()

    def perform_create(self, serializer):
        student = serializer.validated_data["student"]
        class_group = serializer.validated_data["class_group"]
        if serializer.validated_data.get("status", Enrollment.Status.ACTIVE) != Enrollment.Status.ACTIVE:
            raise ValidationError("Uma matrícula nova deve iniciar ativa.")
        try:
            serializer.instance = enroll_student(student=student, class_group_id=class_group.pk)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc

    def perform_update(self, serializer):
        current = serializer.instance
        student = serializer.validated_data.get("student", current.student)
        class_group = serializer.validated_data.get("class_group", current.class_group)
        next_status = serializer.validated_data.get("status", current.status)
        if student.pk != current.student_id or class_group.pk != current.class_group_id:
            raise ValidationError("Para trocar de turma, encerre o vínculo atual e crie outra matrícula.")
        if current.status != Enrollment.Status.ACTIVE and next_status == Enrollment.Status.ACTIVE:
            raise ValidationError("Um vínculo histórico não pode ser reativado; crie uma nova turma/vínculo.")
        serializer.save()


class AssessmentViewSet(ScopedSet):
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Assessment.objects.none()
        user = self.request.user
        queryset = Assessment.objects.select_related("assignment__class_group", "assignment__subject")
        if user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(assignment__class_group__enrollments__student=user.student_profile, status=Assessment.Status.PUBLISHED).distinct()
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(assignment__teacher=user.teacher_profile)
        if user.role == "coordinator" or user.is_superuser:
            return queryset
        return queryset.none()


class GradeViewSet(ScopedSet):
    serializer_class = GradeSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Grade.objects.none()
        user = self.request.user
        queryset = Grade.objects.select_related("assessment__assignment", "enrollment__student__user")
        if user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(enrollment__student=user.student_profile, released_at__isnull=False)
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(assessment__assignment__teacher=user.teacher_profile)
        if user.role == "coordinator" or user.is_superuser:
            return queryset
        return queryset.none()


class AttendanceViewSet(ScopedSet):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()
        user = self.request.user
        queryset = Attendance.objects.select_related("session__assignment", "enrollment__student__user")
        if user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(enrollment__student=user.student_profile)
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(session__assignment__teacher=user.teacher_profile)
        if user.role == "coordinator" or user.is_superuser:
            return queryset
        return queryset.none()


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.none()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")
