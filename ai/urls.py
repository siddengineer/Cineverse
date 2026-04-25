from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='ai-chat'),
    path('recommend/', views.ai_recommend, name='ai-recommend'),
    path('explain/<int:movie_id>/', views.ai_explain, name='ai-explain'),
    path('compare/', views.compare_taste, name='ai-compare'),
    path('list/', views.ai_generate_list, name='ai-list'),
    path('ott/<int:movie_id>/', views.ott_detect, name='ai-ott'),
    path('mood/', views.mood_recommend, name='ai-mood'),
]
