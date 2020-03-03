from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('glasila', views.Glasila, basename='glasila')
router.register('formati', views.Formati, basename='formati')
router.register('dokumenti', views.Dokumenti, basename='dokumenti')
router.register('jezici', views.Jezici, basename='jezici')
router.register('zemlje', views.Zemlje, basename='zemlje')
router.register('podregistri', views.Podregistri, basename='podregistri')
router.register('oblasti', views.Oblasti, basename='oblasti')
router.register('grupe', views.Grupe, basename='grupe')

urlpatterns = [
    # path('glasila/', views.ListGlasila.as_view()),
    path('', include(router.urls)),
]