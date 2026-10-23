from rest_framework.permissions import BasePermission, SAFE_METHODS
class AcademicReadWritePermission(BasePermission):
    def has_permission(self,request,view):
        if not request.user.is_authenticated: return False
        if request.method in SAFE_METHODS: return True
        return request.user.is_superuser or request.user.role in ("admin","coordinator")
