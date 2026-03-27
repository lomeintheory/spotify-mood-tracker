from django.urls import path
from .views import SpotifyAuthSyncView

urlpatterns = [
    path('sync/', SpotifyAuthSyncView.as_view(), name='spotify-auth-sync'),
]