# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# # from rest_framework_simplejwt.views import TokenRefreshView

# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # Auth
#     path('api/auth/', include('users.urls')),
#     # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

#     # Core
#     path('api/movies/', include('movies.urls')),
#     path('api/ratings/', include('movies.rating_urls')),
#     path('api/watchlist/', include('movies.watchlist_urls')),

#     # Features
#     path('api/experience/', include('experience.urls')),
#     path('api/lists/', include('lists.urls')),
#     path('api/ai/', include('ai.urls')),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.shortcuts import render


# def home(request):
#     return render(request, 'index.html')   # serves frontend/index.html


# urlpatterns = [
#     path('', home),

#     path('admin/', admin.site.urls),

#     # Auth
#     path('api/auth/', include('users.urls')),

#     # Core
#     path('api/movies/', include('movies.urls')),
#     path('api/ratings/', include('movies.rating_urls')),
#     path('api/watchlist/', include('movies.watchlist_urls')),

#     # Features
#     path('api/experience/', include('experience.urls')),
#     path('api/lists/', include('lists.urls')),
#     path('api/ai/', include('ai.urls')),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'frontend')






from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/ratings/', include('movies.rating_urls')),
    path('api/watchlist/', include('movies.watchlist_urls')),
    path('api/experience/', include('experience.urls')),
    path('api/lists/', include('lists.urls')),
    path('api/ai/', include('ai.urls')),
] + static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'frontend') \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)