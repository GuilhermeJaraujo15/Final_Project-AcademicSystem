# Arquitetura do projeto

Django é a fonte de autenticação, regras de negócio e esquema; Django REST Framework fornece a API autenticada por sessão. O PostgreSQL é obrigatório no modo normal, configurado por `DATABASE_URL`; `MIGRATION_DATABASE_URL` pode substituir a conexão durante migrações. Não existe fallback SQLite. O modo de preview é isolado e usa backend dummy, sem persistir dados.

Há três perfis acadêmicos: aluno, professor e coordenador. `User` mantém o papel e um índice único parcial limita coordenadores a uma conta. Contas técnicas do Django são mantidas separadamente pela infraestrutura.

`apps.accounts` contém o usuário customizado e o comando protegido de provisionamento. `apps.academics` contém períodos, turmas, disciplinas, atribuições, matrículas, avaliações, entregas, notas, chamadas, conversas, notificações, política institucional e auditoria. `apps.insights` contém agregação de notas e publicações controladas. As regras do modelo e o DER estão em [docs/supabase/DATA_MODEL.md](supabase/DATA_MODEL.md); a preparação PostgreSQL/Supabase está em [docs/supabase/SETUP.md](supabase/SETUP.md).

Rotas API existentes: `/api/v1/students/`, `teachers/`, `subjects/`, `terms/`, `classes/`, `enrollments/`, `assessments/`, `grades/`, `attendance/` e `notifications/`. Schema: `/api/schema/`; Swagger: `/api/docs/`. A API ainda precisa de serviços completos para gravação docente por atribuição, chat, publicação de insights, eventos transacionais de notificação e trilha de auditoria antes de uso operacional.

Para execução local, instale `requirements.txt`, configure segredo e URL PostgreSQL no ambiente, rode `python manage.py check`, revise `python manage.py migrate --plan` e então `python manage.py migrate`. O arquivo `.env.example` documenta os nomes das variáveis; Django não lê `.env` automaticamente. Redis/Celery, e-mail e relatórios têm dependências declaradas, mas os fluxos acadêmicos assíncronos ainda não estão implementados.

O preview visual está descrito em [docs/preview.md](preview.md). Não representa dados reais nem concede permissões.
