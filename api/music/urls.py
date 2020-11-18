from django.urls import path

from .views import ListCreateSongsView, SongDetailsView, LoginView, RegisterUserView

urlpatterns = [
    path('songs', ListCreateSongsView.as_view(), name='all-songs'),
    path('songs/<int:pk>', SongDetailsView.as_view(), name='song-details'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/register', RegisterUserView.as_view(), name='register')
]