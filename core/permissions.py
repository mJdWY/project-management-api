from rest_framework import permissions
from .models import Task
from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsProjectManagerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.manager == request.user

class IsTaskAssigneeOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.assignee == request.user or obj.project.manager == request.user

#################################
class IsProjectMember(permissions.BasePermission): #منشان التعليقات والاشعارات متابعة المهام 
    def has_permission(self, request, view):
        task_id = request.data.get('task') or view.kwargs.get('task_pk') or view.kwargs.get('pk')
        if not task_id:
            return False
        try:
            task = Task.objects.get(id=task_id)
            return request.user in task.project.members.all()
        except:
            return False
#تُستخدم لحماية مهام أو تعليقات أو إشعارات لها علاقة بالمشاريع.
#تمنع أي مستخدم غير مشارك في المشروع من التفاعل مع الكائن
#استخدمتها ب TaskFollowerViewSet، CommentViewSet، NotificationViewSet
"""🧠 مبدأ العمل:

تستخرج ID المهمة (task).

تجلب المهمة من قاعدة البيانات.

تتحقق إن كان المستخدم عضوًا في المشروع المرتبط بها."""
#############
class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.author == request.user


class IsTaskEditor(BasePermission):
    """
    يسمح فقط لمدير المشروع أو الشخص المكلّف بالمهمة أو أحد أعضاء المشروع بتعديل المهمة.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            obj.project.manager == user or
            obj.assignee == user or
            user in obj.project.members.all()
        )