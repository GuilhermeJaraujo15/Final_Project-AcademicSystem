from django.test import SimpleTestCase
from apps.insights.services import predict_dropout_risk
from apps.academics.reports import grades_excel, grades_pdf
from apps.academics.services import attendance_alert_band, grade_alert_band, weighted_average_from_rows
from apps.accounts.models import User
from decimal import Decimal
from types import SimpleNamespace

class PredictionSafetyTests(SimpleTestCase):
    def test_unvalidated_risk_prediction_stays_disabled(self):
        with self.assertRaises(NotImplementedError):
            predict_dropout_risk(object())

class ReportBuilderTests(SimpleTestCase):
    def test_excel_builder_returns_workbook_bytes(self):
        self.assertTrue(grades_excel([]).startswith(b"PK"))

    def test_pdf_builder_returns_pdf_bytes(self):
        self.assertTrue(grades_pdf([]).startswith(b"%PDF"))


class AcademicAlertRuleTests(SimpleTestCase):
    policy = SimpleNamespace(
        attendance_preventive_percent=Decimal("80"),
        attendance_critical_percent=Decimal("75"),
        grade_preventive_percent=Decimal("75"),
        grade_critical_percent=Decimal("70"),
    )

    def test_attendance_threshold_boundary_is_critical_only_below_75(self):
        self.assertEqual(attendance_alert_band(Decimal("80"), self.policy), "preventive")
        self.assertEqual(attendance_alert_band(Decimal("75"), self.policy), "preventive")
        self.assertEqual(attendance_alert_band(Decimal("74.99"), self.policy), "critical")

    def test_grade_average_uses_weights_and_omits_missing_values(self):
        self.assertEqual(
            weighted_average_from_rows([(Decimal("8"), Decimal("10"), Decimal("1")), (Decimal("6"), Decimal("10"), Decimal("3"))]),
            Decimal("6.50"),
        )
        self.assertIsNone(weighted_average_from_rows([]))

    def test_grade_thresholds_are_normalized_to_ten_point_scale(self):
        self.assertEqual(grade_alert_band(Decimal("7.5"), self.policy), "preventive")
        self.assertEqual(grade_alert_band(Decimal("7.0"), self.policy), "critical")

    def test_academic_user_roles_are_exactly_three(self):
        self.assertEqual(
            [role for role, _label in User.Role.choices],
            ["student", "teacher", "coordinator"],
        )
