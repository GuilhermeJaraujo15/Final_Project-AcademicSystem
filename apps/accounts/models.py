from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT="student", "Aluno"
        TEACHER="teacher", "Professor"
        COORDINATOR="coordinator", "Coordenador"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(role__in=["student", "teacher", "coordinator"]), name="user_role_is_academic"),
            models.UniqueConstraint(fields=["role"], condition=Q(role="coordinator"), name="uniq_single_academic_coordinator"),
        ]

    def __str__(self):
        return self.get_full_name() or self.username
