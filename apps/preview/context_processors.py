from django.conf import settings

ROLE_LABELS = {"student": "Aluno", "teacher": "Professor", "coordinator": "Coordenador"}

def demo_context(request):
    role = request.GET.get("role", "coordinator")
    if role not in ROLE_LABELS:
        role = "coordinator"
    return {
        "demo_mode": settings.DEMO_MODE,
        "demo_role": role,
        "demo_role_label": ROLE_LABELS[role],
        "demo_name": {"student": "Marina Costa", "teacher": "Prof. Rafael Lima", "coordinator": "Ana Martins"}[role],
    }
