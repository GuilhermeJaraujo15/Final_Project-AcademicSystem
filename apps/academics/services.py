from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Attendance, AttendanceSession, ClassGroup, Enrollment, Grade, InstitutionalPolicy


@transaction.atomic
def enroll_student(*, student, class_group_id):
    """Create enrollment under a row lock so concurrent requests cannot exceed capacity."""
    class_group = ClassGroup.objects.select_for_update().get(pk=class_group_id)
    existing = Enrollment.objects.filter(student=student, class_group=class_group).first()
    if existing:
        if existing.status != Enrollment.Status.ACTIVE:
            raise ValidationError("Já existe um vínculo histórico para este aluno e turma.")
        return existing
    occupied = Enrollment.objects.filter(class_group=class_group, status=Enrollment.Status.ACTIVE).count()
    if occupied >= class_group.capacity:
        raise ValidationError("A turma atingiu sua capacidade máxima.")
    enrollment = Enrollment(student=student, class_group=class_group)
    enrollment.full_clean()
    enrollment.save()
    return enrollment


def weighted_grade_average(*, enrollment, subject):
    """Return a 0–10 weighted average from released grades; missing grades are omitted."""
    grades = Grade.objects.filter(
        enrollment=enrollment,
        assessment__assignment__subject=subject,
        assessment__assignment__class_group=enrollment.class_group,
        released_at__isnull=False,
    ).values_list("score", "assessment__max_score", "assessment__weight")
    return weighted_average_from_rows(grades)


def weighted_average_from_rows(grades):
    weighted_sum = Decimal("0")
    total_weight = Decimal("0")
    for score, maximum, weight in grades:
        weighted_sum += (score / maximum) * weight
        total_weight += weight
    if not total_weight:
        return None
    return (Decimal("10") * weighted_sum / total_weight).quantize(Decimal("0.01"))


def attendance_percentage(*, enrollment, assignment, policy=None):
    """Use completed calls only; a missing record in a completed call counts as absent."""
    policy = policy or InstitutionalPolicy.objects.get_or_create(singleton_key=1)[0]
    sessions = AttendanceSession.objects.filter(
        assignment=assignment, status=AttendanceSession.Status.HELD,
        finalized_at__isnull=False,
    )
    denominator = sessions.count()
    records = Attendance.objects.filter(enrollment=enrollment, session__in=sessions)
    if not policy.count_excused_absence_in_denominator:
        denominator -= records.filter(status=Attendance.Status.EXCUSED).count()
    if denominator <= 0:
        return None
    present_statuses = [Attendance.Status.PRESENT]
    if policy.count_late_as_present:
        present_statuses.append(Attendance.Status.LATE)
    numerator = records.filter(status__in=present_statuses).count()
    return (Decimal(numerator) * Decimal("100") / Decimal(denominator)).quantize(Decimal("0.01"))


def alert_band(value, *, critical, preventive, critical_is_inclusive):
    """Return critical, preventive or None using centralized policy thresholds."""
    if value is None:
        return None
    is_critical = value <= critical if critical_is_inclusive else value < critical
    if is_critical:
        return "critical"
    if value <= preventive:
        return "preventive"
    return None


def attendance_alert_band(value, policy):
    return alert_band(
        value,
        critical=policy.attendance_critical_percent,
        preventive=policy.attendance_preventive_percent,
        critical_is_inclusive=False,
    )


def grade_alert_band(value, policy):
    # Average uses 0–10; policy thresholds are stored as percentages.
    normalized = Decimal(value) * Decimal("10") if value is not None else None
    return alert_band(
        normalized,
        critical=policy.grade_critical_percent,
        preventive=policy.grade_preventive_percent,
        critical_is_inclusive=True,
    )
