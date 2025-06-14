from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters, status
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsProjectManagerOrReadOnly, IsTaskAssigneeOrManager
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Comment, TaskLog, Notification, TaskFollower


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Comment


from .permissions import IsTaskEditor


from rest_framework.exceptions import PermissionDenied

from .serializers import (
    CommentSerializer, TaskLogSerializer, NotificationSerializer, TaskFollowerSerializer
)
from .permissions import IsCommentAuthorOrReadOnly, IsProjectMember

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectManagerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(members=self.request.user) #هون خليت المدير يشوف كلشي
    def perform_update(self, serializer):
        task = serializer.save()
        task._updated_by = self.request.user  # تمرير المستخدم
        task.save()  # لحفظ الـ updated_by بعد تمريره



        # ✍️ سجل التغييرات
        for field, new_value in serializer.validated_data.items():
            old_value = getattr(task, field, None)
            if str(old_value) != str(new_value):
                TaskLog.objects.create(
                    ask=task,
                    field_changed=field,
                    old_value=old_value,
                    new_value=new_value,
                    changed_by=self.request.user
            )

         # 🔔 إنشاء إشعارات للمتابعين
        followers = TaskFollower.objects.filter(task=task).exclude(user=self.request.user)
        for follower in followers:
            Notification.objects.create(
                user=follower.user,
                message=f'تم تعديل المهمة "{task.title}"',
                 task=task
        )        

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskEditor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'due_date', 'project', 'assignee']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user

        
        # اجلب جميع المشاريع التي هو مدير لها
        managed_projects = Project.objects.filter(manager=user)

        # أو التي هو عضو فيها
        member_projects = Project.objects.filter(members=user)

        # إذا كان المستخدم مديرًا لمشاريع، اجمع كل المهام من المشاريع التي يديرها + المشاريع التي هو عضو فيها
        if managed_projects.exists():
            return Task.objects.filter(project__in=(managed_projects | member_projects).distinct())
        else:
            return Task.objects.filter(project__in=member_projects)
    
    def perform_create(self, serializer):
        # تأكد من أن المستخدم يملك صلاحية إضافة المهمة
        project = serializer.validated_data['project']
        user = self.request.user
        if project.manager != user and user not in project.members.all():
            raise PermissionDenied("You do not have permission to add tasks to this project.")
        serializer.save()

    def perform_update(self, serializer):
        old_instance = Task.objects.get(pk=self.get_object().pk)  # 🟡 نسخة المهمة قبل التعديل

        task = serializer.save()
        task.updated_by = self.request.user
        task.save()

        # 🔵 سجل التغييرات (Logs)
        fields = ['status', 'assignee', 'description']
        for field in fields:
            old_val = getattr(old_instance, field)
            new_val = getattr(task, field)
            if old_val != new_val:
                TaskLog.objects.create(
                task=task,
                changed_by=self.request.user,  # ✅ المستخدم الفعلي الذي عدّل
                field_changed=field,
                old_value=old_val,
                new_value=new_val
            )

        # 🔔 إنشاء إشعارات للمتابعين باستثناء من قام بالتعديل
        followers = TaskFollower.objects.filter(task=task).exclude(user=self.request.user)
        for follower in followers:
            Notification.objects.create(
            user=follower.user,
            message=f'تم تعديل المهمة "{task.title}"',
            task=task
        )




class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

##########################3
from .models import Comment, TaskLog, Notification, TaskFollower

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            # المدير يمكنه رؤية جميع التعليقات
            return Comment.objects.all()
        # المستخدم العادي يرى تعليقاته أو التعليقات المرتبطة بمهام ضمن مشاريع يشارك فيها
        return Comment.objects.filter(
            Q(created_by=user) |
            Q(task__project__participants=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class TaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_pk']
        user = self.request.user

        # ✅ المدير يرى كل السجلات
        if user.is_staff or user.is_superuser:
            return TaskLog.objects.filter(task__id=task_id)

        # ✅ المستخدم العادي يرى فقط السجلات إذا كان عضوًا في المشروع
        return TaskLog.objects.filter(task__id=task_id, task__project__members=user)
    
class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return Response({'status': 'marked as read'})

class TaskFollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        task_id = request.data.get('task')
        task = Task.objects.get(id=task_id)
        if request.user in task.project.members.all():
            TaskFollower.objects.get_or_create(user=request.user, task=task)
            return Response({'status': 'following'})
        return Response({'detail': 'Unauthorized'}, status=403)

    def destroy(self, request, pk=None):
        TaskFollower.objects.filter(task_id=pk, user=request.user).delete()
        return Response({'status': 'unfollowed'})

