# Frontend preview

## Start on Windows PowerShell

From the repository root, run:

```powershell
$env:ACADEMIC_DEMO_MODE = "true"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_SECRET_KEY = "preview-only-local-key"
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`. Stop the server with `Ctrl+C` in its terminal. This mode does not need `DATABASE_URL`, PostgreSQL, Supabase, or credentials.

## Isolation and page map

`ACADEMIC_DEMO_MODE=true` selects a preview-only URL configuration and Django's dummy database backend. Preview views read deterministic fictional records from `apps/preview/data.py`; they do not query or write a database. The normal mode remains unchanged: it requires `DATABASE_URL` for PostgreSQL and uses the existing authenticated dashboard and API routes. No SQLite fallback is present.

The role selector only changes presentation context. It does not log in a user, establish a session, or grant permissions. Preview mode does not expose the admin site or API endpoints. Demo forms use browser validation and local feedback only; they never send a write request.

Routes: `/` dashboard, `/alunos/` and `/alunos/1/`, `/professores/` and `/professores/1/`, `/turmas/` and `/turmas/1/`, `/notas/`, `/frequencia/`, `/acompanhamento/`, `/relatorios/`, and `/administracao/`.

Search, status filters, pagination, role switching, mobile navigation, and modal forms are client-side preview interactions. PDF/Excel controls and advanced analytics are intentionally informational; they do not claim to generate files or predictions.

## Later integration

When PostgreSQL is configured, leave `ACADEMIC_DEMO_MODE` unset or set it to `false`, configure `DATABASE_URL`, apply local migrations, and use the normal Django routes. Reuse the shared templates and replace preview view contexts with permission-scoped database querysets. Keep demo fixtures and the preview URL branch isolated from authenticated API behavior.

## Verification performed

Tailwind compiled with `npm run css:build`. Django system checks passed in preview mode. Three preview route tests passed. Browser checks in Microsoft Edge returned HTTP 200 for every preview page and asset, confirmed role switching, search, pagination, native form validation, zero write requests, no page errors, and no document-level horizontal overflow at 390px width. Desktop and mobile screenshots were inspected. The reference image was not present, so visual matching is based on the written style description.
