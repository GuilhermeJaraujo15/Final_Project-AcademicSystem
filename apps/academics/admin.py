from django.contrib import admin
from .models import *
admin.site.register([Student,Teacher,Term,Subject,ClassGroup,TeachingAssignment,Enrollment,Assessment,Grade,Attendance,Notification,AuditEvent])
