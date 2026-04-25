from django.urls import path
# from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('refresh-taste/', views.refresh_taste_profile, name='refresh-taste'),
    path('user/<str:username>/', views.public_profile, name='public-profile'),
    # path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
]
