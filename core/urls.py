from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TaskViewSet
from django.urls import path, include
from .views import RegisterView, CommentViewSet, TaskLogViewSet, NotificationViewSet, TaskFollowViewSet

from rest_framework_nested.routers import NestedDefaultRouter






router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)

router.register(r'comments', CommentViewSet, basename='comment')
#router.register(r'tasks/(?P<task_pk>\d+)/logs', TaskLogViewSet, basename='task-logs')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'task-follow', TaskFollowViewSet, basename='task-follow')

# ✅ Router المتداخل: logs داخل tasks
task_router = NestedDefaultRouter(router, r'tasks', lookup='task')
task_router.register(r'logs', TaskLogViewSet, basename='task-logs')

# ✅ الجمع بين كل المسارات
urlpatterns = router.urls + task_router.urls
urlpatterns += [
    path('register/', RegisterView.as_view(), name='register'),
]

"""urlpatterns = router.urls
urlpatterns += [
    path('register/', RegisterView.as_view(), name='register'),]
"""