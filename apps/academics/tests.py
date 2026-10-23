from django.test import SimpleTestCase
from apps.insights.services import predict_dropout_risk
from apps.academics.reports import grades_excel, grades_pdf

class PredictionSafetyTests(SimpleTestCase):
    def test_unvalidated_risk_prediction_stays_disabled(self):
        with self.assertRaises(NotImplementedError):
            predict_dropout_risk(object())

class ReportBuilderTests(SimpleTestCase):
    def test_excel_builder_returns_workbook_bytes(self):
        self.assertTrue(grades_excel([]).startswith(b"PK"))

    def test_pdf_builder_returns_pdf_bytes(self):
        self.assertTrue(grades_pdf([]).startswith(b"%PDF"))
