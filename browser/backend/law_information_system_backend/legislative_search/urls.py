from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('glasila', views.Glasila, basename='glasila')

urlpatterns = [
    # path('glasila/', views.ListGlasila.as_view()),
    path('', include(router.urls)),
]