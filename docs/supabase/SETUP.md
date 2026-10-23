# Configurar PostgreSQL/Supabase com Django

Este procedimento apenas prepara o projeto. Nenhuma conexão ou migração remota foi executada nesta etapa.

## 1. Preparar um ambiente revisável

1. Faça backup do banco de destino e confirme ambiente, projeto, organização, branch e credenciais no painel Supabase.
2. Crie um usuário PostgreSQL dedicado à aplicação com privilégio mínimo sobre o schema Django. Não conceda acesso público às tabelas acadêmicas nem use credenciais `service_role` no cliente/frontend.
3. Desative exposição da Data API para tabelas acadêmicas, a menos que uma decisão arquitetural separada defina RLS e identidades compatíveis. A autenticação atual é Django com sessão; não há política `auth.uid()` configurada.
4. Mantenha conexão e credenciais somente em variáveis de ambiente/gerenciador de segredos. O `.env` não é carregado automaticamente pelo Django e não deve ser versionado.

## 2. Configurar variáveis

Copie `.env.example` para um arquivo local ignorado pelo Git ou configure as variáveis no ambiente do processo:

```text
DJANGO_SECRET_KEY=<segredo-forte>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=<hosts-da-aplicacao>
DATABASE_URL=postgresql://<usuario>:<senha-url-encoded>@<host>:5432/<database>?sslmode=require
MIGRATION_DATABASE_URL=postgresql://<usuario-migracao>:<senha-url-encoded>@<host-direto>:5432/<database>?sslmode=require
ACADEMIC_DEMO_MODE=false
```

Use a conexão direta ou o modo de sessão do Supabase para migrações; não use um pooler em modo transaction para operações de schema. `MIGRATION_DATABASE_URL`, quando definida, substitui `DATABASE_URL` como conexão Django naquela execução. As duas URLs devem apontar para o banco e branch revisados. Não coloque URLs em comandos registrados, capturas de tela ou logs.

## 3. Revisar migrações localmente

No ambiente com dependências instaladas e PostgreSQL local de desenvolvimento:

```powershell
$env:DJANGO_SECRET_KEY = '<segredo-local>'
$env:DJANGO_DEBUG = 'true'
$env:DATABASE_URL = 'postgresql://<usuario>:<senha>@localhost:5432/<database>?sslmode=prefer'
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate --check
```

Inspecione o SQL antes de aplicar em qualquer ambiente:

```powershell
python manage.py sqlmigrate accounts 0002
python manage.py sqlmigrate academics 0003
python manage.py sqlmigrate academics 0004
python manage.py sqlmigrate academics 0005
python manage.py sqlmigrate insights 0001
```

A migração do papel legado interrompe a execução se encontrar qualquer papel `admin` legado ou mais de um coordenador. Leia e classifique cada conta, preserve os IDs e altere cada papel para aluno, professor ou coordenador conforme a identidade institucional confirmada antes de reaplicar. Não escolha o coordenador só pelo papel legado; a migração não remove nem promove contas. Atividades sem atribuição inequívoca e frequência sem disciplina permanecem preservadas para revisão.

## 4. Revisão e aplicação em destino

Antes da execução, registre aprovação do plano e backup. Confirme novamente o destino e aplique as migrações versionadas com o mesmo código revisado:

```powershell
python manage.py migrate --plan
python manage.py migrate
python manage.py showmigrations
```

Em execução de migração, defina `MIGRATION_DATABASE_URL` para a conexão direta aprovada, se necessário. Não use `--fake`; a tabela `django_migrations` precisa refletir operações executadas. Depois, use as consultas somente leitura de `VERIFY.sql`, examine constraints/índices e faça um teste de leitura pela aplicação. Não declare sincronização em tempo real por causa do PostgreSQL.

## 5. Provisionar contas

O CSV usa os cabeçalhos `username,email,first_name,last_name,role,student_number,employee_number`. `role` aceita somente `student`, `teacher` e `coordinator`. Aluno precisa de `student_number`; professor de `employee_number`; o coordenador não precisa de identificador docente/aluno. Faça a validação do arquivo fora do banco e proteja-o por conter dados pessoais.

```powershell
python manage.py provision_school_users .\contas-institucionais.csv
```

O comando é atômico, rejeita usernames existentes/repetidos, exige que o estado final tenha exatamente um coordenador e cria senhas inutilizáveis. Ele não inventa nem importa senhas. Use o processo protegido de redefinição/primeiro acesso para cada conta. Nunca inclua senha no CSV.

Crie períodos, quatro turmas com capacidade 30, 11 disciplinas, 11 contas docentes e atribuições docente/turma/disciplina pela rotina administrativa autenticada da próxima fase. Esses cadastros reais não são semeados por esta migração.

## 6. Verificações somente leitura

O arquivo [VERIFY.sql](VERIFY.sql) pode ser executado no SQL Editor para inspecionar conectividade, versão, tabelas Django, constraints, índices e quantidade de coordenadores. Ele não consulta dados pessoais dos estudantes e não altera o banco.
