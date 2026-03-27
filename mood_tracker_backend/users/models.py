from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    spotify_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    spotify_access_token = models.TextField(null=True, blank=True)
    spotify_refresh_token = models.TextField(null=True, blank=True)
    spotify_token_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.spotify_id or self.username
