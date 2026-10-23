from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.academics.models import Enrollment, TeachingAssignment


class InsightPublication(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicado para o aluno"
        INTERNAL = "internal", "Acompanhamento institucional"
        WITHDRAWN = "withdrawn", "Retirado"

    assignment = models.ForeignKey(TeachingAssignment, on_delete=models.PROTECT, related_name="insight_publications")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="insight_publications")
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="insight_publications")
    title = models.CharField(max_length=160)
    summary = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    source_period_start = models.DateField(null=True, blank=True)
    source_period_end = models.DateField(null=True, blank=True)
    source_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["enrollment", "status", "published_at"]), models.Index(fields=["assignment", "created_at"])]

    def clean(self):
        if self.assignment_id and self.enrollment_id and self.assignment.class_group_id != self.enrollment.class_group_id:
            raise ValidationError("O insight e a matrícula devem pertencer à mesma turma.")
        if self.assignment_id and self.published_by_id and self.assignment.teacher.user_id != self.published_by_id:
            raise ValidationError({"published_by": "A publicação deve ser feita pelo professor da atribuição."})
        if self.source_period_start and self.source_period_end and self.source_period_end < self.source_period_start:
            raise ValidationError("O período de origem do insight é inválido.")
