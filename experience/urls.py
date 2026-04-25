from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExperienceListCreateView.as_view(), name='experience-list'),
    path('stats/', views.experience_stats, name='experience-stats'),
    path('<int:pk>/', views.ExperienceDetailView.as_view(), name='experience-detail'),
]
