from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
class Student(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="student_profile")
    student_number=models.CharField(max_length=30,unique=True)
    active=models.BooleanField(default=True)
    def __str__(self): return f"{self.student_number} — {self.user}"
class Teacher(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="teacher_profile")
    employee_number=models.CharField(max_length=30,unique=True)
    def __str__(self): return str(self.user)
class Term(models.Model):
    name=models.CharField(max_length=80,unique=True)
    starts_on=models.DateField(); ends_on=models.DateField()
    def clean(self):
        if self.ends_on < self.starts_on: raise ValidationError("A data final deve ser posterior à inicial.")
    def __str__(self): return self.name
class Subject(models.Model):
    code=models.CharField(max_length=20,unique=True); name=models.CharField(max_length=160); credits=models.PositiveSmallIntegerField(default=0)
    def __str__(self): return f"{self.code} — {self.name}"
class ClassGroup(models.Model):
    code=models.CharField(max_length=30); subject=models.ForeignKey(Subject,on_delete=models.PROTECT,related_name="classes"); term=models.ForeignKey(Term,on_delete=models.PROTECT,related_name="classes"); teachers=models.ManyToManyField(Teacher,through="TeachingAssignment",related_name="classes"); students=models.ManyToManyField(Student,through="Enrollment",related_name="classes")
    class Meta: constraints=[models.UniqueConstraint(fields=["code","term"],name="uniq_class_term")]
    def __str__(self): return f"{self.code} — {self.subject}"
class TeachingAssignment(models.Model):
    teacher=models.ForeignKey(Teacher,on_delete=models.PROTECT); class_group=models.ForeignKey(ClassGroup,on_delete=models.CASCADE,related_name="assignments")
    class Meta: constraints=[models.UniqueConstraint(fields=["teacher","class_group"],name="uniq_teacher_class")]
class Enrollment(models.Model):
    student=models.ForeignKey(Student,on_delete=models.PROTECT,related_name="enrollments"); class_group=models.ForeignKey(ClassGroup,on_delete=models.PROTECT,related_name="enrollments"); enrolled_on=models.DateField(auto_now_add=True); active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["student","class_group"],name="uniq_enrollment")]; indexes=[models.Index(fields=["student","active"])]
class Assessment(models.Model):
    class_group=models.ForeignKey(ClassGroup,on_delete=models.CASCADE,related_name="assessments"); title=models.CharField(max_length=120); max_score=models.DecimalField(max_digits=6,decimal_places=2,default=10); due_on=models.DateField(null=True,blank=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["class_group","title"],name="uniq_assessment_title")]
    def clean(self):
        if self.max_score <= 0: raise ValidationError({"max_score":"A pontuação máxima deve ser positiva."})
class Grade(models.Model):
    assessment=models.ForeignKey(Assessment,on_delete=models.CASCADE,related_name="grades"); enrollment=models.ForeignKey(Enrollment,on_delete=models.CASCADE,related_name="grades"); score=models.DecimalField(max_digits=6,decimal_places=2); recorded_at=models.DateTimeField(auto_now=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["assessment","enrollment"],name="uniq_grade")]
    def clean(self):
        if self.assessment_id and self.enrollment_id and self.assessment.class_group_id != self.enrollment.class_group_id: raise ValidationError("Nota e matrícula devem pertencer à mesma turma.")
        if self.score < 0 or self.assessment_id and self.score > self.assessment.max_score: raise ValidationError("Nota fora da escala permitida.")
class Attendance(models.Model):
    enrollment=models.ForeignKey(Enrollment,on_delete=models.CASCADE,related_name="attendance"); held_on=models.DateField(); present=models.BooleanField(default=True); recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    class Meta: constraints=[models.UniqueConstraint(fields=["enrollment","held_on"],name="uniq_attendance_day")]
class Notification(models.Model):
    recipient=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="notifications"); category=models.CharField(max_length=40); message=models.TextField(); created_at=models.DateTimeField(auto_now_add=True); read_at=models.DateTimeField(null=True,blank=True)
class AuditEvent(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); action=models.CharField(max_length=80); object_type=models.CharField(max_length=80); object_id=models.CharField(max_length=80); created_at=models.DateTimeField(auto_now_add=True); details=models.JSONField(default=dict,blank=True)
