# Arquitetura e decisões

## Estado inicial
O repositório de trabalho estava vazio. O arquivo `TEMA - 8(3).md` e a imagem de referência visual mencionada no briefing não estavam disponíveis no projeto ou na Çrea de trabalho. A implementação segue os requisitos do texto colado e uma identidade institucional azul sóbria; a correspondência visual exata com a referência não pÇde ser validada.

## Módulos
- `apps.accounts`: usuário customizado, papéis e autenticação Django.
- `apps.academics`: alunos, professores, períodos, disciplinas, turmas, matrículas, avaliações, notas, frequência, notificações e auditoria.
- `apps.insights`: agregações e contrato de predição desabilitado até validação empírica.
- `config`: settings, rotas, API versionada e Celery.

Django é autoridade para autenticação, autorização e dados. DRF usa sessão e CSRF. PostgreSQL é obrigatério; `DATABASE_URL` ausente causa erro explÇcito. `MIGRATION_DATABASE_URL` pode apontar conexão direta de migração. Nenhum fallback SQLite é habilitado.

## Modelo conceitual
`User` 1:1 `Student`/`Teacher`; `Subject` 1:N `ClassGroup`; `Term` 1:N `ClassGroup`; `ClassGroup` M:N `Teacher` via `TeachingAssignment` e `Student` via `Enrollment`; `ClassGroup` 1:N `Assessment`; `Enrollment` + `Assessment` 1:N `Grade`; `Enrollment` 1:N `Attendance`; usuário 1:N `Notification` e `AuditEvent`. Restrições únicas impedem duplicação de matrícula, notas por avaliação, frequência diária e atribuição docente.

## Acesso
All API endpoints require an authenticated session. Academic writes are limited to administrators and coordinators. Student and teacher queries are scoped to their academic links. Fine-grained action permissions remain a production hardening item.

## API
`/api/v1/students/`, `teachers/`, `subjects/`, `terms/`, `classes/`, `enrollments/`, `assessments/`, `grades/`, `attendance/`, `notifications/`. Schema: `/api/schema/`; Swagger: `/api/docs/`. Paginação de 25, pesquisa DRF onde configurada.

## Interface e execuÇÇo
Templates Django acessíveis e responsivos com navegação lateral que recolhe em telas pequenas. Tailwind 4 compila de `static/src/input.css` para `static/css/app.css`.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# configure DATABASE_URL para PostgreSQL local (sem Supabase nesta etapa)
python manage.py makemigrations accounts academics
python manage.py migrate
python manage.py createsuperuser
npm install
npm run css:build
python manage.py runserver
```

Carregue variáveis do `.env` no shell/IDE antes de executar; o Django não carrega `.env` automaticamente. Tailwind pode ser verificado com `npm run css:build`. Redis é necessário para worker Celery; configure `REDIS_URL`, então execute `celery -A config worker -l info`. O envio de e-mail requer SMTP.

## Banco futuro
Instale `psycopg`; configure `DATABASE_URL` PostgreSQL com TLS (`sslmode=require`). Para migraÇÇes, `MIGRATION_DATABASE_URL` pode substituir a URL principal. NÇo houve conexão, SQL ou migração remota nesta etapa. Gere e versiona as migraÇÇes localmente apÇs instalar dependências.

## Relatérios, tarefas e predição
ReportLab/pandas/openpyxl/Matplotlib estão declarados; endpoints de geração ainda não implementados. Celery estÇ conectado estruturalmente, sem tarefas acadêmicas registradas ainda. O serviço de predição falha de forma explícita e segura até existir modelo validado e dados adequados. Dashboard usa contagens reais do banco e não dados simulados.

## Pendências conhecidas
Instalar dependências e gerar/validar migraÇÇes; completar formulÇrios CRUD e relatérios; restringir todas as consultas por política de acesso específica; implementar auditoria transacional, tarefas idempotentes e testes; confirmar requisitos detalhados e referência visual assim que `TEMA - 8(3).md` e a imagem estiverem disponíveis. NÇo declare produção pronta.


## Frontend preview

See [preview.md](preview.md) for the isolated, database-free visual preview. Set `ACADEMIC_DEMO_MODE=true` only for that presentation environment. Normal mode still requires PostgreSQL via `DATABASE_URL`.
