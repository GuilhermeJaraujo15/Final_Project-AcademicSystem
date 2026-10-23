from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT="student", "Aluno"
        TEACHER="teacher", "Professor"
        COORDINATOR="coordinator", "Coordenador"
        ADMIN="admin", "Administrador"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True)
    def __str__(self): return self.get_full_name() or self.username
