from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TaskViewSet
from django.urls import path, include
from .views import RegisterView



router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('register/', RegisterView.as_view(), name='register'),
]
