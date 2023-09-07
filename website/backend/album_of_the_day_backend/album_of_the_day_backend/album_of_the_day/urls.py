"""album_of_the_day URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
import rest_framework.urls, rest_framework.authtoken.views, rest_framework.routers
from rest_framework.schemas import get_schema_view
from website.views import *
import dotenv

API_VERSION = "1.0.0"  # Constant, the API version.
# Import .env variables if possibly defined (also see asgi.py)
dotenv.load_dotenv("./../.backend.env", verbose=True)
# Run tasks
from .startup import run_startup_tasks

run_startup_tasks()
urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api/", include(rest_framework.urls)),  # For the REST API
    path(
        "api/schema",
        get_schema_view(
            title="Album of the day API",
            description="An API for retrieving saved album of the days, albums, genres, and album lists.",
            version=API_VERSION,
        ),
    ),
    path(
        "login/token/", rest_framework.authtoken.views.obtain_auth_token
    ),  # For obtaining an authorization token
    path("api/albums", AlbumView.as_view()),
    path("api/albums/<int:pk>", IndividualAlbumView.as_view()),
    path("api/artists", ArtistView.as_view()),
    path("api/artists/<int:pk>", IndividualArtistView.as_view()),
    path("api/genres", GenreView.as_view()),
    path("api/genres/<int:pk>", IndividualGenreView.as_view()),
    path("api/album-of-the-days", AlbumOfTheDayView.as_view()),
    path("api/album-of-the-days/<int:pk>", IndividualAlbumOfTheDayView.as_view()),
    path("api/lists", AlbumListView.as_view()),
    path("api/lists/<int:pk>", IndividualAlbumListView.as_view()),
    path("api/daily-rotations", DailyRotationView.as_view()),
    path("api/daily-rotations/<int:pk>", IndividualDailyRotationView.as_view()),
    path("api/<str:item>/available_months", ItemAvailableMonthsView.as_view()),
    path("api/statistics", AllTimeStatisticsView.as_view()),
    path("spotify", GetSpotifyAuthenticationStatusView.as_view()),
    path("spotify/auth", spotify_authentication_view),
    path("spotify/callback", spotify_callback_view),
    path("spotify/toggle", ToggleAlbumStatusInSpotifyView.as_view()),
    path("spotify/album/status", GetAlbumAddedToSpotifyView.as_view()),
]
