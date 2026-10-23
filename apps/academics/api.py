from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Student,Teacher,Subject,Term,ClassGroup,Enrollment,Assessment,Grade,Attendance,Notification
from .serializers import *
from .permissions import AcademicReadWritePermission
class ScopedSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated,AcademicReadWritePermission]
class StudentViewSet(ScopedSet):
    serializer_class=StudentSerializer; search_fields=["student_number","user__first_name","user__last_name"]
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Student.objects.none()
        qs=Student.objects.select_related("user")
        if self.request.user.role=="student": return qs.filter(user=self.request.user)
        if self.request.user.role=="teacher": return qs.filter(enrollments__class_group__teachers__user=self.request.user).distinct()
        return qs
class TeacherViewSet(ScopedSet): queryset=Teacher.objects.select_related("user"); serializer_class=TeacherSerializer; search_fields=["employee_number","user__first_name","user__last_name"]
class SubjectViewSet(ScopedSet): queryset=Subject.objects.all(); serializer_class=SubjectSerializer; search_fields=["code","name"]
class TermViewSet(ScopedSet): queryset=Term.objects.all(); serializer_class=TermSerializer
class ClassGroupViewSet(ScopedSet):
    serializer_class=ClassGroupSerializer; search_fields=["code","subject__name"]
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return ClassGroup.objects.none()
        u=self.request.user; qs=ClassGroup.objects.select_related("subject","term")
        if u.role=="student" and hasattr(u,"student_profile"): return qs.filter(enrollments__student=u.student_profile)
        if u.role=="teacher" and hasattr(u,"teacher_profile"): return qs.filter(teachers=u.teacher_profile)
        return qs
class EnrollmentViewSet(ScopedSet):
    serializer_class=EnrollmentSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Enrollment.objects.none()
        u=self.request.user; qs=Enrollment.objects.select_related("student__user","class_group")
        if u.role=="student" and hasattr(u,"student_profile"): return qs.filter(student=u.student_profile)
        if u.role=="teacher" and hasattr(u,"teacher_profile"): return qs.filter(class_group__teachers=u.teacher_profile)
        return qs
class AssessmentViewSet(ScopedSet):
    serializer_class=AssessmentSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Assessment.objects.none()
        u=self.request.user; qs=Assessment.objects.select_related("class_group")
        if u.role=="student" and hasattr(u,"student_profile"): return qs.filter(class_group__enrollments__student=u.student_profile).distinct()
        if u.role=="teacher" and hasattr(u,"teacher_profile"): return qs.filter(class_group__teachers=u.teacher_profile)
        return qs
class GradeViewSet(ScopedSet):
    serializer_class=GradeSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Grade.objects.none()
        u=self.request.user; qs=Grade.objects.select_related("assessment","enrollment__student__user")
        if u.role=="student" and hasattr(u,"student_profile"): return qs.filter(enrollment__student=u.student_profile)
        if u.role=="teacher" and hasattr(u,"teacher_profile"): return qs.filter(assessment__class_group__teachers=u.teacher_profile)
        return qs
class AttendanceViewSet(ScopedSet):
    serializer_class=AttendanceSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Attendance.objects.none()
        u=self.request.user; qs=Attendance.objects.select_related("enrollment__student__user")
        if u.role=="student" and hasattr(u,"student_profile"): return qs.filter(enrollment__student=u.student_profile)
        if u.role=="teacher" and hasattr(u,"teacher_profile"): return qs.filter(enrollment__class_group__teachers=u.teacher_profile)
        return qs
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Notification.objects.none()
    serializer_class=NotificationSerializer; permission_classes=[IsAuthenticated]
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user).order_by("-created_at")
