from rest_framework import serializers
from apps.accounts.models import User
from .models import Student, Teacher, Subject, Term, ClassGroup, Enrollment, Assessment, Grade, Attendance, Notification

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.Role.STUDENT), write_only=True)
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    class Meta:
        model = Student
        fields = ["id", "user", "student_number", "name", "active"]

class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.Role.TEACHER), write_only=True)
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    class Meta:
        model = Teacher
        fields = ["id", "user", "employee_number", "name"]

class SubjectSerializer(serializers.ModelSerializer):
    class Meta: model = Subject; fields = "__all__"

class TermSerializer(serializers.ModelSerializer):
    class Meta: model = Term; fields = "__all__"
    def validate(self, attrs):
        start = attrs.get("starts_on", getattr(self.instance, "starts_on", None))
        end = attrs.get("ends_on", getattr(self.instance, "ends_on", None))
        if start and end and end < start: raise serializers.ValidationError("A data final deve ser posterior a data inicial.")
        return attrs

class ClassGroupSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class Meta: model = ClassGroup; fields = ["id", "code", "subject", "subject_name", "term"]

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta: model = Enrollment; fields = "__all__"

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta: model = Assessment; fields = "__all__"
    def validate_max_score(self, value):
        if value <= 0: raise serializers.ValidationError("A pontuacao maxima deve ser positiva.")
        return value

class GradeSerializer(serializers.ModelSerializer):
    class Meta: model = Grade; fields = "__all__"
    def validate(self, attrs):
        assessment = attrs.get("assessment", getattr(self.instance, "assessment", None))
        enrollment = attrs.get("enrollment", getattr(self.instance, "enrollment", None))
        score = attrs.get("score", getattr(self.instance, "score", None))
        if assessment and enrollment and assessment.class_group_id != enrollment.class_group_id:
            raise serializers.ValidationError("Nota e matricula devem pertencer na mesma turma.")
        if score is not None and (score < 0 or assessment and score > assessment.max_score):
            raise serializers.ValidationError("Nota fora da escala permitida.")
        return attrs

class AttendanceSerializer(serializers.ModelSerializer):
    recorded_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta: model = Attendance; fields = "__all__"
    def validate(self, attrs):
        enrollment = attrs.get("enrollment", getattr(self.instance, "enrollment", None))
        held_on = attrs.get("held_on", getattr(self.instance, "held_on", None))
        if enrollment and not enrollment.active: raise serializers.ValidationError("A matricula nao esta ativa.")
        return attrs

class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model = Notification; fields = ["id", "category", "message", "created_at", "read_at"]
