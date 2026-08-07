from rest_framework import permissions
from accounts.enums import UserRole


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            UserRole.TEACHER,
            UserRole.ADMIN,
        )


class IsEducationOfficerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            UserRole.EDUCATION_OFFICER,
            UserRole.ADMIN,
        )


class IsFinanceOfficerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == (
            UserRole.FINANCE_OFFICER,
            UserRole.ADMIN,
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user == obj.owner_user
            or request.user.role == UserRole.ADMIN
        )


class IsResponsibleOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user == obj.owner_user
            or request.user.role == UserRole.ADMIN
        )
