from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListCreateView.as_view(), name='list-list'),
    path('mine/', views.MyListsView.as_view(), name='my-lists'),
    path('<int:pk>/', views.ListDetailView.as_view(), name='list-detail'),
    path('<int:list_id>/add/', views.add_movie_to_list, name='list-add-movie'),
    path('<int:list_id>/remove/', views.remove_movie_from_list, name='list-remove-movie'),
    path('<int:list_id>/like/', views.toggle_like_list, name='list-like'),
]
