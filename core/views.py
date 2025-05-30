from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsProjectManagerOrReadOnly, IsTaskAssigneeOrManager
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .serializers import RegisterSerializer
from django.contrib.auth.models import User


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

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskAssigneeOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'due_date', 'project', 'assignee']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Task.objects.filter(project__members=self.request.user)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
