from rest_framework.routers import DefaultRouter
from .api import *
router=DefaultRouter()
for prefix,view,name in [("students",StudentViewSet,"student"),("teachers",TeacherViewSet,"teacher"),("subjects",SubjectViewSet,"subject"),("terms",TermViewSet,"term"),("classes",ClassGroupViewSet,"class"),("enrollments",EnrollmentViewSet,"enrollment"),("assessments",AssessmentViewSet,"assessment"),("grades",GradeViewSet,"grade"),("attendance",AttendanceViewSet,"attendance"),("notifications",NotificationViewSet,"notification")]: router.register(prefix,view,basename=name)
urlpatterns=router.urls
