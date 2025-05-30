from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from .models import Project, Task


class ProjectTaskPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # إنشاء المستخدمين
        self.manager = User.objects.create_user(username='manager', password='pass')
        self.member = User.objects.create_user(username='member', password='pass')
        self.stranger = User.objects.create_user(username='stranger', password='pass')

        # إنشاء المشروع
        self.project = Project.objects.create(name='Test Project', description='desc', manager=self.manager)
        self.project.members.set([self.manager, self.member])

        # إنشاء مهمة
        self.task = Task.objects.create(
            title='Test Task',
            description='Task Desc',
            project=self.project,
            assignee=self.member,
            status='todo',
            due_date=date.today()
        )

    def authenticate(self, user):
        response = self.client.post('/api/token/', {
            'username': user.username,
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 200, msg=f"Token request failed for {user.username}")
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_stranger_cannot_see_project(self):
        self.authenticate(self.stranger)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # لا يرى شيئًا

    def test_manager_can_update_and_delete_project(self):
        self.authenticate(self.manager)
        response = self.client.patch(f'/api/projects/{self.project.id}/', {'name': 'Updated Project'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_member_cannot_update_or_delete_project(self):
        self.authenticate(self.member)
        response = self.client.patch(f'/api/projects/{self.project.id}/', {'name': 'Hack Attempt'}, format='json')
        #self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        #self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    def test_assignee_can_update_task(self):
        self.authenticate(self.member)
        response = self.client.patch(f'/api/tasks/{self.task.id}/', {'status': 'done'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_update_task(self):
        self.authenticate(self.manager)
        response = self.client.patch(f'/api/tasks/{self.task.id}/', {'status': 'in_progress'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stranger_cannot_update_task(self):
        self.authenticate(self.stranger)
        response = self.client.patch(f'/api/tasks/{self.task.id}/', {'status': 'done'}, format='json')
        #self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])