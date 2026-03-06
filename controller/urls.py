from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('start/', views.start_system),
    path('stop/', views.stop_system),
    path('video/', views.video_feed),
]
