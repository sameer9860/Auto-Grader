from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to ADMIN only"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

class TeacherRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to ADMIN and TEACHER"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'TEACHER']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to authenticated students (and staff)"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'TEACHER', 'STUDENT']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()
