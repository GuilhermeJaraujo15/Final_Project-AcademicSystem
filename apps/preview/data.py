"""Small, deterministic, fictional records used only by the visual preview."""

STUDENTS = [
    {"id": 1, "name": "Marina Costa", "number": "2026-0142", "course": "Engenharia de Software", "class": "ES-3A", "status": "Ativo", "email": "marina.costa@example.test", "average": "8,7", "attendance": "94%"},
    {"id": 2, "name": "Lucas Almeida", "number": "2026-0188", "course": "Engenharia de Software", "class": "ES-3A", "status": "Ativo", "email": "lucas.almeida@example.test", "average": "7,9", "attendance": "89%"},
    {"id": 3, "name": "Beatriz Oliveira", "number": "2025-0971", "course": "Sistemas de Informação", "class": "SI-2B", "status": "Acompanhamento", "email": "beatriz.oliveira@example.test", "average": "5,8", "attendance": "73%"},
    {"id": 4, "name": "Pedro Santos", "number": "2026-0204", "course": "Engenharia de Software", "class": "ES-3A", "status": "Ativo", "email": "pedro.santos@example.test", "average": "8,1", "attendance": "91%"},
    {"id": 5, "name": "Sofia Ribeiro", "number": "2024-0643", "course": "Ciência de Dados", "class": "CD-4A", "status": "Inativo", "email": "sofia.ribeiro@example.test", "average": "—", "attendance": "—"},
    {"id": 6, "name": "Gabriel Ferreira", "number": "2025-1110", "course": "Sistemas de Informação", "class": "SI-2B", "status": "Ativo", "email": "gabriel.ferreira@example.test", "average": "7,2", "attendance": "86%"},
    {"id": 7, "name": "Clara Mendes", "number": "2026-0249", "course": "Ciência de Dados", "class": "CD-1A", "status": "Ativo", "email": "clara.mendes@example.test", "average": "9,1", "attendance": "98%"},
]
TEACHERS = [
    {"id": 1, "name": "Rafael Lima", "number": "DOC-018", "area": "Engenharia de Software", "classes": "ES-3A, ES-2A", "status": "Ativo", "email": "rafael.lima@example.test"},
    {"id": 2, "name": "Camila Rocha", "number": "DOC-026", "area": "Matemática Aplicada", "classes": "ES-3A, CD-1A", "status": "Ativo", "email": "camila.rocha@example.test"},
    {"id": 3, "name": "André Carvalho", "number": "DOC-031", "area": "Banco de Dados", "classes": "SI-2B, CD-4A", "status": "Ativo", "email": "andre.carvalho@example.test"},
    {"id": 4, "name": "Juliana Alves", "number": "DOC-044", "area": "Estatística", "classes": "CD-1A, CD-4A", "status": "Ativo", "email": "juliana.alves@example.test"},
]
CLASSES = [
    {"id": 1, "code": "ES-3A", "subject": "Arquitetura de Software", "term": "2026 - 1º semestre", "teacher": "Rafael Lima", "students": "32", "status": "Em andamento"},
    {"id": 2, "code": "SI-2B", "subject": "Banco de Dados II", "term": "2026 - 1º semestre", "teacher": "André Carvalho", "students": "28", "status": "Em andamento"},
    {"id": 3, "code": "CD-1A", "subject": "Estatística Aplicada", "term": "2026 - 1º semestre", "teacher": "Juliana Alves", "students": "30", "status": "Em andamento"},
    {"id": 4, "code": "CD-4A", "subject": "Aprendizado de Máquina", "term": "2025 - 2º semestre", "teacher": "Camila Rocha", "students": "25", "status": "Encerrada"},
]
GRADES = [
    {"student": "Marina Costa", "class": "ES-3A", "assessment": "Projeto de arquitetura", "score": "9,2", "date": "14 out 2026"},
    {"student": "Lucas Almeida", "class": "ES-3A", "assessment": "Projeto de arquitetura", "score": "8,4", "date": "14 out 2026"},
    {"student": "Beatriz Oliveira", "class": "SI-2B", "assessment": "Avaliação prática", "score": "5,8", "date": "13 out 2026"},
    {"student": "Pedro Santos", "class": "ES-3A", "assessment": "Projeto de arquitetura", "score": "8,7", "date": "12 out 2026"},
]
ATTENDANCE = [
    {"student": "Marina Costa", "class": "ES-3A", "sessions": "17 / 18", "rate": "94%", "status": "Regular"},
    {"student": "Lucas Almeida", "class": "ES-3A", "sessions": "16 / 18", "rate": "89%", "status": "Regular"},
    {"student": "Beatriz Oliveira", "class": "SI-2B", "sessions": "11 / 15", "rate": "73%", "status": "Atenção"},
    {"student": "Pedro Santos", "class": "ES-3A", "sessions": "16 / 18", "rate": "91%", "status": "Regular"},
]
ALERTS = [
    {"student": "Beatriz Oliveira", "type": "Frequência abaixo do esperado", "detail": "73% de presença em Banco de Dados II", "priority": "Atenção", "date": "Hoje, 09:40"},
    {"student": "Lucas Almeida", "type": "Avaliação pendente", "detail": "Projeto de arquitetura aguardando revisão", "priority": "Pendente", "date": "Ontem, 15:20"},
    {"student": "Marina Costa", "type": "Acompanhamento concluído", "detail": "Registro pedagógico atualizado", "priority": "Concluído", "date": "20 out 2026"},
]
