from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework_jwt.settings import api_settings
from rest_framework import permissions

from .models import Song
from .serializers import SongSerializer
from .decorators import validate_request_data
from .serializers import TokenSerializer
from .serializers import UserSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class RegisterUserView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        if not username or not password or not email:
            return Response(
                data={
                    'message': 'Username, email and password are required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        new_user = User.objects.create_user(username=username,email=email,password=password)
        return Response(
            data={
                'user': UserSerializer(new_user).data
            },
            status=status.HTTP_201_CREATED
        )  


class LoginView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            serializer = TokenSerializer(data={
                'token': jwt_encode_handler(jwt_payload_handler(user))
            })
            serializer.is_valid()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            data={
                'message': 'Invalid credentials'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )    


class ListCreateSongsView(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        songs = self.queryset.order_by('title')
        return Response(
            data={
                'songs': SongSerializer(songs, many=True).data
            },
            status=status.HTTP_200_OK
        )

    @validate_request_data
    def post(self, request, *args, **kwargs):
        song = Song.objects.create(
            title=request.data['title'],
            artist=request.data['artist']
        )

        return Response(
            data={
                'song': SongSerializer(song).data
            },
            status=status.HTTP_201_CREATED
        )

    
class SongDetailsView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Song.objects.all()
    serializer_class = SongSerializer

    def get(self, request, *args, **kwargs):
        try:
            song = self.queryset.get(pk=kwargs['pk'])
            return Response(
                data={
                    'song': SongSerializer(song).data
                },
                status=status.HTTP_200_OK
            )
        except Song.DoesNotExist:
            return Response(
                data={
                    'message': f"Song with id: {kwargs['pk']} does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    @validate_request_data
    def put(self, request, *args, **kwargs):
        try:
            song = self.queryset.get(pk=kwargs['pk'])
            update_song = SongSerializer().update(song, request.data)
            return Response(
                data={
                    'song': SongSerializer(update_song).data
                },
                status=status.HTTP_200_OK
            )

        except Song.DoesNotExist:
            return Response(
                data={
                    'message': f"Song with id: {kwargs['pk']} does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            song = self.queryset.get(pk=kwargs['pk'])
            song.delete()
            return Response(
                data={
                    'message': f"Song with id: {kwargs['pk']} is deleted"
                },
                status=status.HTTP_204_NO_CONTENT
            )

        except Song.DoesNotExist:
            return Response(
                data={
                    'message': f"Song with id: {kwargs['pk']} does not exist"
                },
                status=status.HTTP_404_NOT_FOUND
            )    