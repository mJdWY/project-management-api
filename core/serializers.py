from rest_framework import serializers
from .models import Project, Task, Comment, TaskLog, Notification, TaskFollower
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='assignee')
    updated_by_Name=serializers.StringRelatedField(source='updated_by', read_only=True)
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['updated_by']

class ProjectSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='manager')
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True, source='members')

    class Meta:
        model = Project
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'email', 'password']
        read_only_fields = ('id',)
    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user
################################################
class CommentSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_at','created_by']

class TaskLogSerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = TaskLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class TaskFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFollower
        fields = '__all__'
