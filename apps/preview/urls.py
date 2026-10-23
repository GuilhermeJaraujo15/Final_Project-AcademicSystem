from django.urls import path
from . import views

app_name = "preview"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("alunos/", views.listing, {"section": "students"}, name="students"),
    path("alunos/<int:object_id>/", views.detail, {"section": "students"}, name="student-detail"),
    path("professores/", views.listing, {"section": "teachers"}, name="teachers"),
    path("professores/<int:object_id>/", views.detail, {"section": "teachers"}, name="teacher-detail"),
    path("turmas/", views.listing, {"section": "classes"}, name="classes"),
    path("turmas/<int:object_id>/", views.detail, {"section": "classes"}, name="class-detail"),
    path("notas/", views.section, {"section": "grades"}, name="grades"),
    path("frequencia/", views.section, {"section": "attendance"}, name="attendance"),
    path("acompanhamento/", views.section, {"section": "monitoring"}, name="monitoring"),
    path("relatorios/", views.section, {"section": "reports"}, name="reports"),
    path("administracao/", views.section, {"section": "administration"}, name="administration"),
]
