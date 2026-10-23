from django.http import Http404
from django.shortcuts import render
from . import data

NAV = {
    "grades": {"title": "Notas e avaliações", "subtitle": "Resultados individuais e visão de desempenho por turma.", "columns": ["student", "class", "assessment", "score", "date"], "rows": data.GRADES, "label": "Registrar avaliação"},
    "attendance": {"title": "Frequência", "subtitle": "Acompanhamento de presença por estudante e turma.", "columns": ["student", "class", "sessions", "rate", "status"], "rows": data.ATTENDANCE, "label": "Registrar frequência"},
    "monitoring": {"title": "Acompanhamento acadêmico", "subtitle": "Alertas para apoiar o acompanhamento pedagógico.", "columns": ["student", "type", "detail", "priority", "date"], "rows": data.ALERTS, "label": "Novo registro"},
}
LISTS = {
    "students": {"title": "Alunos", "subtitle": "Cadastro e acompanhamento dos estudantes.", "columns": ["name", "number", "course", "class", "average", "attendance", "status"], "rows": data.STUDENTS, "label": "Cadastrar aluno"},
    "teachers": {"title": "Professores", "subtitle": "Corpo docente e vínculos acadêmicos.", "columns": ["name", "number", "area", "classes", "email", "status"], "rows": data.TEACHERS, "label": "Cadastrar professor"},
    "classes": {"title": "Turmas e disciplinas", "subtitle": "Turmas, períodos letivos e responsáveis.", "columns": ["code", "subject", "term", "teacher", "students", "status"], "rows": data.CLASSES, "label": "Criar turma"},
}

def dashboard(request):
    return render(request, "preview/dashboard.html", {"page_title": "Visão geral", "active_nav": "dashboard", "metrics": [("Estudantes ativos", "1.284", "+ 4,2% no período"), ("Turmas em andamento", "48", "6 cursos acompanhados"), ("Frequência média", "91,6%", "Dados demonstrativos"), ("Avaliações lançadas", "326", "Neste semestre")], "recent_grades": data.GRADES[:3], "alerts": data.ALERTS[:2], "course_rates": [("Engenharia de Software", "93%", 93), ("Sistemas de Informação", "89%", 89), ("Ciência de Dados", "92%", 92)]})

def listing(request, section):
    config = LISTS.get(section)
    if not config: raise Http404
    return render(request, "preview/list.html", {**config, "section": section, "columns": [(key, {"name": "Nome", "number": "Matrícula / ID", "course": "Curso", "class": "Turma", "average": "Média", "attendance": "Frequência", "status": "Situação", "area": "área", "classes": "Vínculos", "email": "E-mail", "code": "Turma", "subject": "Disciplina", "term": "Período", "teacher": "Professor", "students": "Alunos"}.get(key, key.title())) for key in config["columns"]], "active_nav": section, "page_title": config["title"], "detail_name": {"students": "preview:student-detail", "teachers": "preview:teacher-detail", "classes": "preview:class-detail"}[section], "columns_label": {"name": "Nome", "number": "Matrícula / ID", "course": "Curso", "class": "Turma", "average": "Média", "attendance": "Frequência", "status": "Situação", "area": "área", "classes": "Vínculos", "email": "E-mail", "code": "Turma", "subject": "Disciplina", "term": "Período", "teacher": "Professor", "students": "Alunos"}})

def detail(request, section, object_id):
    records = {"students": data.STUDENTS, "teachers": data.TEACHERS, "classes": data.CLASSES}.get(section, [])
    record = next((item for item in records if item["id"] == object_id), None)
    if not record: raise Http404
    title_key = {"students": "name", "teachers": "name", "classes": "code"}[section]
    return render(request, "preview/detail.html", {"record": record, "record_items": [(key.replace("_", " ").title(), value) for key, value in record.items() if key != "id"], "page_title": record[title_key], "subtitle": {"students": "Perfil demonstrativo do estudante", "teachers": "Perfil demonstrativo do docente", "classes": "Resumo demonstrativo da turma"}[section], "active_nav": section})

def section(request, section):
    if section in NAV:
        return render(request, "preview/list.html", {**NAV[section], "section": section, "columns": [(key, {"student": "Estudante", "class": "Turma", "assessment": "Avaliação", "score": "Nota", "date": "Data", "sessions": "Presenças", "rate": "Frequência", "status": "Situação", "type": "Tipo de alerta", "detail": "Detalhe", "priority": "Prioridade"}.get(key, key.title())) for key in NAV[section]["columns"]], "active_nav": section, "page_title": NAV[section]["title"], "columns_label": {"student": "Estudante", "class": "Turma", "assessment": "Avaliação", "score": "Nota", "date": "Data", "sessions": "Presenças", "rate": "Frequência", "status": "Situação", "type": "Tipo de alerta", "detail": "Detalhe", "priority": "Prioridade"}, "visual_only": True})
    config = {
        "reports": {"title": "Relatórios", "subtitle": "Selecione critérios para preparar uma consulta demonstrativa.", "cards": [("Desempenho por turma", "Notas, médias e avaliações no período."), ("Frequência individual", "Presenças e ausências por estudante."), ("Resumo acadêmico", "Indicadores consolidados por curso.")]},
        "administration": {"title": "Administração", "subtitle": "Visão conceitual de papéis e configurações institucionais.", "cards": [("Administrador", "Gerencia usuários e configurações do sistema."), ("Coordenador", "Acompanha cursos, turmas e resultados."), ("Professor", "Consulta suas turmas e registra atividades."), ("Aluno", "Acompanha os próprios vínculos e resultados.")]},
    }
    config = config.get(section)
    if not config: raise Http404
    return render(request, "preview/section.html", {**config, "section": section, "active_nav": section, "page_title": config["title"], "visual_only": True})
