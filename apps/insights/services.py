"""Analysis contracts. Risk inference stays disabled until a validated model exists."""
from django.db.models import Avg, Count
from apps.academics.models import Grade

def class_grade_summary(class_group):
    return Grade.objects.filter(assessment__class_group=class_group).aggregate(mean=Avg("score"), graded=Count("id"))

def predict_dropout_risk(enrollment):
    raise NotImplementedError("PrevisÇes ficam desabilitadas até existir modelo treinado e validado.")
