from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ClassGroup, Student, Teacher, Enrollment
@login_required
def dashboard(request):
    user=request.user
    groups=ClassGroup.objects.none()
    if user.is_superuser or user.role == "coordinator": groups=ClassGroup.objects.select_related("term").prefetch_related("assignments__subject").all()
    elif user.role == "teacher" and hasattr(user,"teacher_profile"): groups=user.teacher_profile.classes.select_related("term").prefetch_related("assignments__subject")
    elif user.role == "student" and hasattr(user,"student_profile"): groups=user.student_profile.classes.select_related("term").prefetch_related("assignments__subject")
    context={"groups":groups[:8],"group_count":groups.count(),"student_count":Student.objects.count() if user.is_superuser or user.role == "coordinator" else None,"teacher_count":Teacher.objects.count() if user.is_superuser or user.role == "coordinator" else None,"enrollment_count":Enrollment.objects.filter(class_group__in=groups).count()}
    return render(request,"academics/dashboard.html",context)
