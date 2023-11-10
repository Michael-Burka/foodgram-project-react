from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls', namespace='foodgram_user')),
    path('api/', include('foodgram_api.urls', namespace='api'))
]

