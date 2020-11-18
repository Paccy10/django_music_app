import json
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.contrib.auth.models import User

from .models import Song
from .serializers import SongSerializer

class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_song(title='', artist=''):
        if title != '' and artist != '':
            Song.objects.create(title=title,artist=artist)

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='test_user',
            email='test@mail.com',
            password='testing',
            first_name='test',
            last_name='user',
        )
        self.create_song('like glue', 'sean paul')
        self.create_song('simple song', 'konshens')
        self.create_song('love is wicked', 'brick and lace')
        self.create_song('jam rock', 'damien marley')

    def login_client(self, username='', password=''):
        response = self.client.post(reverse('create-token'),
                                    data=json.dumps({'username': username, 'password': password}),
                                    content_type='application/json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.client.login(username=username, password=password)

        return self.token

class RegisterUserTest(BaseViewTest):

    def test_register_user_succeeds(self):
        user = {
            'username': 'beyonce', 
            'email': 'beyonce@gmail.com',
            'password': 'password'
        }
        response = self.client.post(
            reverse('register'), 
            data=json.dumps(user),
            content_type='application/json')
        user['id'] = 2
        del user['password']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], user)  

    def test_register_user_fails(self):
        response = self.client.post(
            reverse('register'),
            content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Username, email and password are required')


class LoginUserTest(BaseViewTest):

    def test_login_user_succeeds(self):
        response = self.client.post(reverse('login'),
                                    data=json.dumps({'username': 'test_user', 'password': 'testing'}),
                                    content_type='application/json')   

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_fails(self):
        response = self.client.post(reverse('login'),
                                    data=json.dumps({'username': 'anonymous', 'password': 'testing'}),
                                    content_type='application/json')   

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetAllSongsTest(BaseViewTest):

    def test_get_all_songs_succeeds(self):
        self.login_client('test_user', 'testing')
        response = self.client.get(reverse('all-songs'))
        songs = Song.objects.all().order_by('title')
        serialized_songs = SongSerializer(songs, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['songs'], serialized_songs.data)

class CreateSongTest(BaseViewTest):

    def test_create_song_succeeds(self):
        self.login_client('test_user', 'testing')
        song = {
            'title': 'hello', 
            'artist': 'beyonce'
        }
        response = self.client.post(
            reverse('all-songs'), 
            data=json.dumps(song),
            content_type='application/json')
        song['id'] = 5

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['song'], song)  

    def test_create_song_fails(self):
        self.login_client('test_user', 'testing')
        response = self.client.post(
            reverse('all-songs'),
            content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Both title and artist are required')

class GetSingleSongTest(BaseViewTest):

    def test_get_single_song_succeeds(self):
        response = self.client.get(reverse('song-details', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['song'], 
                        {'id': 1, 'title': 'like glue', 'artist': 'sean paul'})

    def test_get_single_song_fails(self):
        response = self.client.get(reverse('song-details', kwargs={'pk': 10}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Song with id: 10 does not exist')

class UpdateSongTest(BaseViewTest):

    def test_update_song(self):
        self.login_client('test_user', 'testing')
        song = {
            'title': 'the vow', 
            'artist': 'bull dogg'
        }
        response = self.client.put(
            reverse('song-details', kwargs={'pk': 1}),
            data=json.dumps(song),
            content_type='application/json')

        song['id'] = 1    

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['song'], song)

class DeleteSongTest(BaseViewTest):

    def test_delete_song(self):
        self.login_client('test_user', 'testing')
        response = self.client.delete(reverse('song-details', kwargs={'pk': 1}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Song with id: 1 is deleted')

        