from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()

SYNC_URL = reverse('spotify-auth-sync')

MOCK_PROFILE = {
    'id': 'spotify_user_123',
    'display_name': 'Test User',
    'email': 'test@example.com',
}


def mock_spotify_response(status_code=200, profile=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = profile or MOCK_PROFILE
    return resp


class SpotifyAuthSyncViewTests(APITestCase):

    def test_missing_access_token_returns_400(self):
        response = self.client.post(SYNC_URL, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    @patch('users.views.requests.get')
    def test_invalid_spotify_token_returns_401(self, mock_get):
        mock_get.return_value = mock_spotify_response(status_code=401)
        response = self.client.post(SYNC_URL, {'access_token': 'bad_token'}, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.data)

    @patch('users.views.requests.get')
    def test_new_user_returns_201_and_created_flag(self, mock_get):
        mock_get.return_value = mock_spotify_response()
        response = self.client.post(SYNC_URL, {'access_token': 'valid_token'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['created'])
        self.assertIn('token', response.data)
        self.assertEqual(response.data['spotify_id'], MOCK_PROFILE['id'])

    @patch('users.views.requests.get')
    def test_new_user_profile_fields_are_stored(self, mock_get):
        mock_get.return_value = mock_spotify_response()
        self.client.post(SYNC_URL, {'access_token': 'valid_token'}, format='json')

        user = User.objects.get(spotify_id=MOCK_PROFILE['id'])
        self.assertEqual(user.username, MOCK_PROFILE['id'])
        self.assertEqual(user.email, MOCK_PROFILE['email'])
        self.assertEqual(user.first_name, MOCK_PROFILE['display_name'])
        self.assertEqual(user.spotify_access_token, 'valid_token')

    @patch('users.views.requests.get')
    def test_existing_user_returns_200_and_updates_tokens(self, mock_get):
        mock_get.return_value = mock_spotify_response()
        self.client.post(SYNC_URL, {'access_token': 'old_token'}, format='json')

        mock_get.return_value = mock_spotify_response()
        response = self.client.post(SYNC_URL, {'access_token': 'new_token'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['created'])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            User.objects.get(spotify_id=MOCK_PROFILE['id']).spotify_access_token,
            'new_token',
        )

    @patch('users.views.requests.get')
    def test_same_api_token_returned_on_repeated_logins(self, mock_get):
        mock_get.return_value = mock_spotify_response()
        first = self.client.post(SYNC_URL, {'access_token': 'token_v1'}, format='json')

        mock_get.return_value = mock_spotify_response()
        second = self.client.post(SYNC_URL, {'access_token': 'token_v2'}, format='json')

        self.assertEqual(first.data['token'], second.data['token'])
