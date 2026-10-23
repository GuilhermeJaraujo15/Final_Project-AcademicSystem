-- Read-only checks for Supabase SQL Editor. No student data is selected.
SELECT current_database() AS database_name,
       current_user AS connected_role,
       current_setting('server_version') AS postgres_version;

SELECT schemaname, tablename
FROM pg_catalog.pg_tables
WHERE schemaname = 'public'
  AND (tablename LIKE 'academics_%' OR tablename LIKE 'accounts_%' OR tablename LIKE 'insights_%')
ORDER BY tablename;

SELECT n.nspname AS schema_name,
       c.relname AS table_name,
       con.conname AS constraint_name,
       con.contype AS constraint_type,
       pg_catalog.pg_get_constraintdef(con.oid) AS definition
FROM pg_catalog.pg_constraint con
JOIN pg_catalog.pg_class c ON c.oid = con.conrelid
JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('accounts_user', 'academics_classgroup', 'academics_teachingassignment',
                    'academics_enrollment', 'academics_assessment', 'academics_submission',
                    'academics_grade', 'academics_attendancesession', 'academics_attendance',
                    'academics_notification', 'academics_conversation')
ORDER BY c.relname, con.conname;

SELECT schemaname, tablename, indexname, indexdef
FROM pg_catalog.pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('accounts_user', 'academics_classgroup', 'academics_teachingassignment',
                    'academics_enrollment', 'academics_assessment', 'academics_submission',
                    'academics_grade', 'academics_attendancesession', 'academics_attendance',
                    'academics_notification')
ORDER BY tablename, indexname;

SELECT role, count(*) AS account_count
FROM public.accounts_user
WHERE role IN ('student', 'teacher', 'coordinator')
GROUP BY role
ORDER BY role;

SELECT count(*) AS coordinator_count,
       count(*) = 1 AS exactly_one_coordinator
FROM public.accounts_user
WHERE role = 'coordinator';

SELECT count(*) AS applied_migrations
FROM public.django_migrations
WHERE app IN ('accounts', 'academics', 'insights');
