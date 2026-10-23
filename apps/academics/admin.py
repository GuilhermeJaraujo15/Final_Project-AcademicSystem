from django.contrib import admin
from .models import *
admin.site.register([
    Student, Teacher, Term, Subject, ClassGroup, TeachingAssignment, Enrollment,
    Assessment, Submission, Grade, Topic, AssessmentTopic, AttendanceSession,
    Attendance, InstitutionalPolicy, Conversation, ChatMessage, Notification,
    AuditEvent,
])
