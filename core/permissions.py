from rest_framework import permissions

class IsProjectManagerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.manager == request.user

class IsTaskAssigneeOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.assignee == request.user or obj.project.manager == request.user
