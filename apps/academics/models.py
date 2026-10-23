from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="student_profile")
    student_number = models.CharField(max_length=30, unique=True)
    active = models.BooleanField(default=True)

    def clean(self):
        if self.user_id and self.user.role != self.user.Role.STUDENT:
            raise ValidationError({"user": "O perfil acadêmico deve pertencer a uma conta de aluno."})

    def __str__(self):
        return f"{self.student_number} — {self.user}"


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="teacher_profile")
    employee_number = models.CharField(max_length=30, unique=True)

    def clean(self):
        if self.user_id and self.user.role != self.user.Role.TEACHER:
            raise ValidationError({"user": "O perfil acadêmico deve pertencer a uma conta de professor."})

    def __str__(self):
        return str(self.user)


class Term(models.Model):
    name = models.CharField(max_length=80, unique=True)
    starts_on = models.DateField()
    ends_on = models.DateField()

    def clean(self):
        if self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "A data final deve ser igual ou posterior à inicial."})

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=160)
    credits = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.code} — {self.name}"


class ClassGroup(models.Model):
    code = models.CharField(max_length=30)
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="classes")
    capacity = models.PositiveSmallIntegerField(default=30)
    legacy_subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.PROTECT, related_name="legacy_classes", help_text="Disciplina do esquema anterior; não usar para novas atribuições.")
    teachers = models.ManyToManyField(Teacher, through="TeachingAssignment", related_name="classes")
    students = models.ManyToManyField(Student, through="Enrollment", related_name="classes")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["code", "term"], name="uniq_class_term"), models.CheckConstraint(condition=Q(capacity__gt=0), name="class_capacity_positive")]

    def __str__(self):
        return f"{self.code} — {self.term}"


class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="assignments")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="assignments")
    active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["teacher", "class_group", "subject"], name="uniq_teacher_class_subject")]
        indexes = [models.Index(fields=["teacher", "active"]), models.Index(fields=["class_group", "subject"])]

    def clean(self):
        if self.teacher_id and self.teacher.user.role != self.teacher.user.Role.TEACHER:
            raise ValidationError({"teacher": "A atribuição exige um perfil de professor."})

    def __str__(self):
        return f"{self.teacher} — {self.subject} — {self.class_group}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativa"
        COMPLETED = "completed", "Concluída"
        WITHDRAWN = "withdrawn", "Transferida/encerrada"

    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="enrollments")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.PROTECT, related_name="enrollments")
    enrolled_on = models.DateField(auto_now_add=True)
    ended_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "class_group"], name="uniq_enrollment")]
        indexes = [models.Index(fields=["student", "status"]), models.Index(fields=["class_group", "status"])]

    @property
    def active(self):
        return self.status == self.Status.ACTIVE


class Assessment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicada"
        CLOSED = "closed", "Encerrada"

    assignment = models.ForeignKey(TeachingAssignment, null=True, blank=True, on_delete=models.PROTECT, related_name="assessments")
    legacy_class_group = models.ForeignKey(ClassGroup, null=True, blank=True, on_delete=models.PROTECT, related_name="legacy_assessments")
    due_on = models.DateField(null=True, blank=True, help_text="Prazo legado, mantido para registros anteriores.")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=10)
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    due_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assignment", "title"], name="uniq_assessment_title_assignment"), models.CheckConstraint(condition=Q(max_score__gt=0), name="assessment_positive_max_score"), models.CheckConstraint(condition=Q(weight__gt=0), name="assessment_positive_weight"), models.CheckConstraint(condition=Q(status="draft") | Q(assignment__isnull=False), name="published_assessment_requires_assignment")]
        indexes = [models.Index(fields=["assignment", "status", "due_at"])]

    @property
    def class_group(self):
        if self.assignment_id:
            return self.assignment.class_group
        return self.legacy_class_group

    def clean(self):
        if self.max_score is not None and self.max_score <= 0:
            raise ValidationError({"max_score": "A pontuação máxima deve ser positiva."})


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        SUBMITTED = "submitted", "Entregue"
        LATE = "late", "Entregue em atraso"
        RETURNED = "returned", "Devolvida para correção"

    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT, related_name="submissions")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="submissions")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    content = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assessment", "enrollment"], name="uniq_submission_assessment_enrollment")]
        indexes = [models.Index(fields=["enrollment", "status"])]

    def clean(self):
        if self.assessment_id and self.enrollment_id and self.assessment.assignment_id and self.assessment.assignment.class_group_id != self.enrollment.class_group_id:
            raise ValidationError("A entrega e a matrícula devem pertencer à mesma turma.")


class Grade(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT, related_name="grades")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="grades")
    score = models.DecimalField(max_digits=6, decimal_places=2)
    feedback = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="recorded_grades")
    recorded_at = models.DateTimeField(auto_now=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assessment", "enrollment"], name="uniq_grade"), models.CheckConstraint(condition=Q(score__gte=0), name="grade_nonnegative")]
        indexes = [models.Index(fields=["enrollment", "released_at"])]

    def clean(self):
        if self.assessment_id and self.enrollment_id and self.assessment.assignment_id and self.assessment.assignment.class_group_id != self.enrollment.class_group_id:
            raise ValidationError("A nota e a matrícula devem pertencer à mesma turma.")
        if self.score is not None and self.assessment_id and self.score > self.assessment.max_score:
            raise ValidationError({"score": "A nota excede a pontuação máxima."})


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="topics")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["subject", "name"], name="uniq_topic_subject_name")]


class AssessmentTopic(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.PROTECT, related_name="topic_links")
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name="assessment_links")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assessment", "topic"], name="uniq_assessment_topic")]

    def clean(self):
        if self.assessment_id and self.topic_id and self.assessment.assignment_id and self.assessment.assignment.subject_id != self.topic.subject_id:
            raise ValidationError("O tópico precisa pertencer à disciplina da atividade.")


class AttendanceSession(models.Model):
    class Status(models.TextChoices):
        HELD = "held", "Realizada"
        CANCELLED = "cancelled", "Cancelada"
        EXCLUDED = "excluded", "Não contabilizada"

    assignment = models.ForeignKey(TeachingAssignment, null=True, blank=True, on_delete=models.PROTECT, related_name="attendance_sessions")
    held_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.HELD)
    topic = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assignment", "held_at"], name="uniq_attendance_assignment_datetime")]
        indexes = [models.Index(fields=["assignment", "status", "held_at"])]


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Presente"
        ABSENT = "absent", "Ausente"
        LATE = "late", "Atrasado"
        EXCUSED = "excused", "Falta justificada"

    session = models.ForeignKey(AttendanceSession, null=True, blank=True, on_delete=models.PROTECT, related_name="records")
    held_on = models.DateField(null=True, blank=True, help_text="Data legada sem sessão; mantida para preservar registros anteriores.")
    present = models.BooleanField(default=True, help_text="Valor legado; registros novos usam status e session.")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="attendance")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    justification = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="attendance_records")
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["session", "enrollment"], condition=Q(session__isnull=False), name="uniq_attendance_session_enrollment"), models.CheckConstraint(condition=Q(session__isnull=False) | Q(held_on__isnull=False), name="attendance_session_or_legacy_date_required")]
        indexes = [models.Index(fields=["enrollment", "status"])]

    def clean(self):
        if self.session_id and self.enrollment_id and self.session.assignment_id and self.session.assignment.class_group_id != self.enrollment.class_group_id:
            raise ValidationError("A chamada e a matrícula devem pertencer à mesma turma.")


class InstitutionalPolicy(models.Model):
    singleton_key = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    attendance_preventive_percent = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    attendance_critical_percent = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    grade_preventive_percent = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    grade_critical_percent = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    count_late_as_present = models.BooleanField(default=True)
    count_excused_absence_in_denominator = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(singleton_key=1), name="institutional_policy_singleton"),
            models.CheckConstraint(condition=Q(attendance_critical_percent__gte=0, attendance_critical_percent__lte=100, attendance_preventive_percent__gte=0, attendance_preventive_percent__lte=100, grade_critical_percent__gte=0, grade_critical_percent__lte=100, grade_preventive_percent__gte=0, grade_preventive_percent__lte=100), name="institutional_policy_valid_thresholds"),
            models.CheckConstraint(condition=Q(attendance_critical_percent__lt=F("attendance_preventive_percent")), name="policy_attendance_critical_below_preventive"),
            models.CheckConstraint(condition=Q(grade_critical_percent__lte=F("grade_preventive_percent")), name="policy_grade_critical_at_or_below_preventive"),
        ]

    def clean(self):
        if self.attendance_critical_percent >= self.attendance_preventive_percent:
            raise ValidationError("O limite crítico de frequência deve ser menor que o preventivo.")
        if self.grade_critical_percent > self.grade_preventive_percent:
            raise ValidationError("O limite crítico de desempenho deve ser menor ou igual ao preventivo.")


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="notifications")
    category = models.CharField(max_length=60)
    title = models.CharField(max_length=160, blank=True, default="")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    dedupe_key = models.CharField(max_length=200, blank=True)
    target_path = models.CharField(max_length=300, blank=True)
    related_object_type = models.CharField(max_length=80, blank=True)
    related_object_id = models.CharField(max_length=80, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["recipient", "dedupe_key"], condition=~Q(dedupe_key=""), name="uniq_notification_recipient_dedupe")]
        indexes = [models.Index(fields=["recipient", "created_at"]), models.Index(fields=["recipient", "read_at", "created_at"])]


class Conversation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="conversations")
    assignment = models.ForeignKey(TeachingAssignment, on_delete=models.PROTECT, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "assignment"], name="uniq_student_assignment_conversation")]

    def clean(self):
        if self.student_id and self.assignment_id and not self.assignment.class_group.enrollments.filter(student_id=self.student_id, status=Enrollment.Status.ACTIVE).exists():
            raise ValidationError("O aluno precisa estar matriculado na turma da atribuição.")


class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.PROTECT, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="chat_messages")
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sent_at", "id"]
        indexes = [models.Index(fields=["conversation", "sent_at"])]

    def clean(self):
        if not self.conversation_id or not self.sender_id:
            return
        conversation = self.conversation
        allowed_ids = {conversation.student.user_id, conversation.assignment.teacher.user_id}
        if self.sender_id not in allowed_ids:
            raise ValidationError({"sender": "Somente o aluno e o professor da conversa podem enviar mensagens."})


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="audit_events")
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["object_type", "object_id", "created_at"]), models.Index(fields=["actor", "created_at"])]
