from django.test import SimpleTestCase, override_settings

@override_settings(DEMO_MODE=True, ROOT_URLCONF="apps.preview.test_urls")
class PreviewRoutesTests(SimpleTestCase):
    def test_academic_preview_pages_render_without_database_data(self):
        for path in ["/", "/alunos/", "/alunos/1/", "/professores/", "/professores/1/", "/turmas/", "/turmas/1/", "/notas/", "/frequencia/", "/acompanhamento/", "/relatorios/", "/administracao/"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_role_switch_only_changes_demonstration_context(self):
        response = self.client.get("/alunos/?role=student")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Marina Costa")
        self.assertContains(response, 'value="student" selected')

    def test_unknown_role_falls_back_to_coordinator_view(self):
        response = self.client.get("/?role=superuser")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Martins")

    def test_institutional_configuration_page_shows_only_academic_profiles(self):
        response = self.client.get("/administracao/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coordenador")
        self.assertContains(response, "Professor")
        self.assertContains(response, "Aluno")
        self.assertNotContains(response, "Administrador")
