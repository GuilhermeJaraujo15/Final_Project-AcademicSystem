import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.academics.models import Student, Teacher


class Command(BaseCommand):
    help = "Provisiona contas acadêmicas a partir de CSV validado, sem criar ou importar senhas."

    def add_arguments(self, parser):
        parser.add_argument("csv_file")

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        try:
            with open(options["csv_file"], "r", encoding="utf-8-sig", newline="") as source:
                rows = list(csv.DictReader(source))
        except OSError as exc:
            raise CommandError(f"Não foi possível ler o CSV: {exc}") from exc
        if not rows:
            raise CommandError("O CSV não contém registros.")

        required = {"username", "email", "first_name", "last_name", "role"}
        if not required.issubset(rows[0]):
            raise CommandError("Colunas obrigatórias: username,email,first_name,last_name,role; alunos precisam student_number e professores employee_number.")
        normalized = [{key: (value or "").strip() for key, value in row.items()} for row in rows]
        usernames = [row["username"] for row in normalized]
        if not all(usernames) or len(set(usernames)) != len(usernames):
            raise CommandError("Usernames devem estar preenchidos e ser únicos no arquivo.")

        coordinator_rows = [row for row in normalized if row["role"] == User.Role.COORDINATOR]
        coordinator_exists = User.objects.filter(role=User.Role.COORDINATOR).exists()
        if len(coordinator_rows) + int(coordinator_exists) != 1:
            raise CommandError("O lote deve manter exatamente uma conta de coordenador: inclua uma na carga inicial ou preserve a existente.")
        valid_roles = {choice for choice, _ in User.Role.choices}
        student_numbers = [row.get("student_number", "") for row in normalized if row["role"] == User.Role.STUDENT]
        employee_numbers = [row.get("employee_number", "") for row in normalized if row["role"] == User.Role.TEACHER]
        if len(set(student_numbers)) != len(student_numbers) or Student.objects.filter(student_number__in=student_numbers).exists():
            raise CommandError("Há números de matrícula duplicados ou já cadastrados.")
        if len(set(employee_numbers)) != len(employee_numbers) or Teacher.objects.filter(employee_number__in=employee_numbers).exists():
            raise CommandError("Há números funcionais duplicados ou já cadastrados.")
        for row in normalized:
            if row["role"] not in valid_roles:
                raise CommandError(f"Papel acadêmico inválido para {row['username']}: {row['role']}")
            if row["role"] == User.Role.STUDENT and not row.get("student_number"):
                raise CommandError(f"student_number obrigatório para {row['username']}.")
            if row["role"] == User.Role.TEACHER and not row.get("employee_number"):
                raise CommandError(f"employee_number obrigatório para {row['username']}.")
            if row["role"] == User.Role.COORDINATOR and (row.get("student_number") or row.get("employee_number")):
                raise CommandError("A conta do coordenador não deve conter identificador de aluno ou professor.")
            if User.objects.filter(username=row["username"]).exists():
                raise CommandError(f"Já existe uma conta com username {row['username']}.")

        for row in normalized:
            user = User.objects.create_user(
                username=row["username"],
                email=row.get("email", ""),
                first_name=row.get("first_name", ""),
                last_name=row.get("last_name", ""),
                role=row["role"],
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])
            if user.role == User.Role.STUDENT:
                Student.objects.create(user=user, student_number=row["student_number"])
            elif user.role == User.Role.TEACHER:
                Teacher.objects.create(user=user, employee_number=row["employee_number"])
        self.stdout.write(self.style.SUCCESS(f"{len(normalized)} contas provisionadas sem senhas definidas."))
