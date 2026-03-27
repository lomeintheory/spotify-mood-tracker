import requests
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

User = get_user_model()

SPOTIFY_ME_URL = 'https://api.spotify.com/v1/me'


class SpotifyAuthSyncView(APIView):
    """
    Called by NextAuth after a successful Spotify OAuth login.
    Verifies the token against Spotify, then upserts the local user
    and returns a DRF auth token for subsequent API requests.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        refresh_token = request.data.get('refresh_token')
        expires_at = request.data.get('expires_at')

        if not access_token:
            return Response(
                {'error': 'access_token is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        spotify_resp = requests.get(
            SPOTIFY_ME_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=5,
        )
        if spotify_resp.status_code != 200:
            return Response(
                {'error': 'Invalid or expired Spotify token'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        profile = spotify_resp.json()
        spotify_id = profile['id']
        display_name = profile.get('display_name') or ''
        email = profile.get('email') or ''

        token_expires_at = None
        if expires_at:
            token_expires_at = datetime.fromtimestamp(int(expires_at), tz=timezone.utc)

        user, created = User.objects.update_or_create(
            spotify_id=spotify_id,
            defaults={
                'username': spotify_id,
                'email': email,
                'first_name': display_name,
                'spotify_access_token': access_token,
                'spotify_refresh_token': refresh_token or '',
                'spotify_token_expires_at': token_expires_at,
            },
        )

        api_token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                'token': api_token.key,
                'user_id': user.pk,
                'spotify_id': user.spotify_id,
                'created': created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )