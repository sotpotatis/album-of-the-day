import datetime
import logging
import secrets, sys

import pytz
from django.shortcuts import render
from .models import *
from .permissions import IsAllowedToEdit
from rest_framework.response import Response
from rest_framework import mixins, generics, views, permissions
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

# from url_filter.integrations.drf import DjangoFilterBackend
from filters.mixins import FiltersMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from typing import List, Dict, Optional, Type
from django.db.models import Model, Prefetch
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from spotify_api_client.client import (
    SpotifyClient,
    SpotifyUser,
    SpotifyScope,
    SpotifyAPIException,
    SpotifyDataNotFound,
    SpotifyAuthenticationRevoked,
)
from django.utils.crypto import get_random_string
from enum import Enum
from .api_exceptions import (
    BadRequestException,
    NotFoundException,
    InternalServerErrorException,
)

logger = logging.getLogger(__name__)


OBJECT_TO_SEARCHABLE_FIELDS = {  # Mapping: object --> searchable field
    Album: ["name", "id", ("genres", Genre)],
    Artist: ["name", "id"],
    Genre: ["name", "id"],
    AlbumList: ["name", "id", "description", ("items", AlbumListItem)],
    AlbumListItem: [("album", Album), "comments", "heading", "body"],
    DailyRotation: ["day", "id", "description"],
}


def generate_searchable_parameters(
    internal_fields: List, external_fields: Dict[str, Model]
):
    """For the Django search API, you can not specify searchable fields
    that are ManyToManyField or ForeignKeys without setting what the searchable attributes of those
    fields are. Since I'm reusing relationships, this function will be able to generate
    and centralize what the searchable parameters for each model are and generate a list with
    these parameters.

    :param internal_fields The internal fields that should be searchable in a view.

    :param external_fields The IDs of any external fields that should be searchable in a view.
    For example, if a model has a list of Genre(s) under the key "genre", you can pass
    {"genres": Genre} to generate the searchable parameters."""
    searchable_parameters = internal_fields
    for external_key, external_object_type in external_fields.items():
        # Get the searchable fields for each object type
        for searchable_field in OBJECT_TO_SEARCHABLE_FIELDS[external_object_type]:
            if isinstance(searchable_field, str):
                searchable_parameters.append(f"{external_key}__{searchable_field}")
            else:  # Allow nesting relationships - somewhat hacky, but whatever:)
                searchable_parameters.extend(
                    generate_searchable_parameters(
                        [],
                        {f"{external_key}__{searchable_field[0]}": searchable_field[1]},
                    )
                )
    return searchable_parameters


def generate_filter_mappings_from_searchable_parameters(
    searchable_parameters: List[str], extensions: Optional[Dict[str, List[str]]] = None
) -> Dict[str, str]:
    """To allow filtering across relationships from the API via URL parameters, I tried a million packages
    (all were unsupported) until I found this one: https://github.com/manjitkumar/drf-url-filters
    which does work with the latest Django version. This package requires each viewset to have a parameter
    called filter_mappings to map a URL parameter to a database parameter to access.
    This function uses the return from the generate_searchable_parameters function and creates a dictionary from it.
    It's very simple: essentially what this function does is takes a list and converts it into a dictionary:
    ["foo","bar"] --> {"foo": "foo", "bar": "bar"}.

    :param searchable_parameters: Return from generate_searchable_parameters.

    :param extensions: Optional parameter. If you need more fields for a certain data type, for example, you need the "gte", "lte" and "exact" matches on a date,
    you can specify them here like this: {"date": ["exact", "lte", "gte"]}, and the function will return "date__exact","date__lte" and "date__gte" instead of just
    "date".

    :returns A dictionary that can be used with the package drf-url-filters."""
    if extensions is None:  # Fill out defaults
        extensions = {}
    result = {}
    for searchable_parameter in searchable_parameters:
        if searchable_parameter not in extensions:
            result[searchable_parameter] = searchable_parameter
        else:
            for extension in extensions[searchable_parameter]:
                extended_parameter = f"{searchable_parameter}__{extension}"
                result[extended_parameter] = extended_parameter
    return result


# Define an index view
def index(request):
    logger.info("Index page requested. Returning content...")
    return render(request, "index.html")


# Define views for all the models
# The ListCreateAPIView is a generic list view of multiple objects.
# The APIView is used for custom views.
# FilterMixin together with the attribute filter_mappings
# is added to some views for filtering via URL parameters
def attrs_to_prefetches(attrs):
    prefetches = []
    for attr in attrs:
        prefetches.append(Prefetch(attr, to_attr=f"{attr}_list"))
    return prefetches


class AlbumView(FiltersMixin, generics.ListCreateAPIView):
    """Lists all albums that are in the database."""

    queryset = Album.objects.prefetch_related(*(ALBUM_RELATED_FIELDS))
    serializer_class = AlbumSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ["artists", "genres"]
    search_fields = generate_searchable_parameters(
        ["name", "id"], {"artists": Artist, "genres": Genre}
    )
    filter_mappings = generate_filter_mappings_from_searchable_parameters(search_fields)


class IndividualAlbumView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves an individual album."""

    queryset = Album.objects.prefetch_related(*(ALBUM_RELATED_FIELDS))
    serializer_class = AlbumSerializer


class ArtistView(generics.ListCreateAPIView):
    """Lists all artists that are in the database."""

    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "id"]
    search_fields = OBJECT_TO_SEARCHABLE_FIELDS[Artist]


class IndividualArtistView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves an individual artist."""

    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


class GenreView(generics.ListCreateAPIView):
    """Lists all genres that are in the database."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "id"]
    search_fields = OBJECT_TO_SEARCHABLE_FIELDS[Genre]


class IndividualGenreView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves an individual genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class AlbumOfTheDayView(FiltersMixin, generics.ListCreateAPIView):
    """Lists all albums of the day that are in the database."""

    queryset = AlbumOfTheDay.objects.prefetch_related(*ALBUM_OF_THE_DAY_RELATED_FIELDS)
    serializer_class = AlbumOfTheDaySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    ordering = ["-date"]
    search_fields = generate_searchable_parameters(
        ["date", "comments"], {"album": Album}
    )
    filter_mappings = generate_filter_mappings_from_searchable_parameters(
        search_fields, {"date": ["gte", "lte", "exact"]}
    )


class IndividualAlbumOfTheDayView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves an individual album of the day."""

    queryset = AlbumOfTheDay.objects.prefetch_related(*ALBUM_OF_THE_DAY_RELATED_FIELDS)
    serializer_class = AlbumOfTheDaySerializer


class AlbumListView(FiltersMixin, generics.ListCreateAPIView):
    """Lists all album lists that are in the database."""

    queryset = AlbumList.objects.prefetch_related(*ALBUM_LIST_RELATED_FIELDS)
    serializer_class = AlbumListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "id"]
    search_fields = generate_searchable_parameters(
        ["name", "id"], {"items": AlbumListItem}
    )
    filter_mappings = generate_filter_mappings_from_searchable_parameters(search_fields)


class IndividualAlbumListView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves an individual album list."""

    queryset = AlbumList.objects.all()
    serializer_class = AlbumListSerializer


class DailyRotationView(FiltersMixin, generics.ListCreateAPIView):
    """Lists all daily rotations that are in the database."""

    queryset = DailyRotation.objects.prefetch_related(*DAILY_ROTATION_RELATED_FIELDS)
    serializer_class = DailyRotationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["day", "id"]
    search_fields = generate_searchable_parameters(
        ["day", "id"], {"genres": Genre, "albums": Album}
    )
    filter_mappings = generate_filter_mappings_from_searchable_parameters(
        search_fields, {"day": ["gte", "lte", "exact"]}
    )


class IndividualDailyRotationView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves an individual daily rotation."""

    queryset = DailyRotation.objects.all()
    serializer_class = DailyRotationSerializer


class AllTimeStatisticsView(views.APIView):
    """Shows an overview of statistics of all time, such as how many albums that
    is in the database etc."""

    def get(self, *args, **kwargs):
        """Respond with the all time statistics."""
        entries = [
            ("album_of_the_day", AlbumOfTheDay),  # Mapping: ID --> model
            ("album", Album),
            ("list", AlbumList),
            ("genre", Genre),
            ("artist", Artist),
            ("daily_rotation", DailyRotation),
        ]
        # Generate the counts
        logger.info("Generating counts for all-time statistics...")
        response_json = {"count": {}}
        for entry_id, entry_object in entries:
            response_json["count"][entry_id] = len(entry_object.objects.all())
        return Response(response_json)


class ItemAvailableMonthsView(views.APIView):
    """Get all the years and months that there are available album of the days
    or daily rotations for."""

    def get(self, request, item, *args, **kwargs):
        ITEMS_TO_MODEL: Dict[
            str, Type[Model]
        ] = {  # Mapping: item URL parameter --> model name
            "album-of-the-days": AlbumOfTheDay,
            "daily-rotations": DailyRotation,
        }
        logger.info("Got a request to get all available item months.")
        # Validate the item key
        requested_item = item.lower()
        if requested_item not in ITEMS_TO_MODEL:
            raise BadRequestException(
                f"Invalid \"item\" key: please use one of {','.join(ITEMS_TO_MODEL)}"
            )
        requested_model = ITEMS_TO_MODEL[requested_item]
        requested_items = requested_model.objects.all()
        response_json: Dict[str, List[int]] = {}
        response_json_ordered: OrderedDict[str, List[int]] = OrderedDict()
        # Create the response JSON: unordered
        for item in requested_items:
            if requested_model == AlbumOfTheDay:
                model_date = item.date
            elif requested_model == DailyRotation:
                model_date = item.day
            model_year = str(model_date.year)
            model_month = model_date.month
            if model_year not in response_json:
                response_json[model_year] = []
            if model_month not in response_json[model_year]:
                response_json[model_year].append(model_month)
        # Order the response JSON
        year_order = list(response_json.keys())
        year_order.sort(key=lambda year: int(year), reverse=True)
        for year in year_order:
            response_json_ordered[year] = response_json[year]
            response_json_ordered[year].sort(reverse=True)
        return Response(response_json_ordered)


# Custom views created for "save to Spotify"
# This is a function where the user can save any album to their Spotify
# profile for later.
def get_saved_spotify_profile_from_request(
    request: HttpRequest, source: Optional[str] = None
) -> Optional[SavedSpotifyUser]:
    """Retrieves a profile based of a token that is connected to a Spotify account (if any).
    Token is set as a URL query parameter.
    If the token is not set or does not link to an active account, None is returned.
    NOTE: You have to prevalidate that spotify_token exists in request.GET before calling this function.

    :param request The incoming request from Django.

    :param source: Where to get the token from. "cookies" to get it in cookies, "url" to get it from the URL parameter. Optional
    value, default is "cookies"
    """
    logger.info("Checking for saved Spotify token from request...")
    # The "source" argument allows us to get the token from a certain source (see above).
    # Here, we retrieve it.
    VALID_SOURCE_ARGUMENT_VALUES = ["cookies", "url"]
    if source is None:
        source = "cookies"  # Default is to get in cookies
    if source == "cookies":
        cookie_token = request.COOKIES.get(
            "spotify_token", None
        )  # Get token from cookies
    elif source == "url":
        cookie_token = request.GET.get(
            "spotify_token", None
        )  # Get token from URL parameters
    else:
        raise ValueError(
            f"Invalid source type requested: \"{source}\" (must be one of: {','.join(VALID_SOURCE_ARGUMENT_VALUES)}"
        )
    if cookie_token is None:
        logger.info("Did not find Spotify profile: no cookie token included/passed.")
        return None
    spotify_profile = SavedSpotifyUser.objects.filter(cookie_token=cookie_token).first()
    spotify_user = None
    if spotify_profile is not None:
        logger.info("Found Spotify profile. Validating that it exists...")
        try:
            spotify_user = get_spotify_user_from_saved(spotify_profile)
            return spotify_profile
        except SpotifyAuthenticationRevoked:
            logger.warning(
                "Authentication was revoked. Removing the user from the database..."
            )
            spotify_profile.delete()
            logger.info("The user was deleted.")
    else:
        logger.warning(
            f"A Spotify token was found in the cookies/URL, but it did not match a public profile! (token: {cookie_token})"
        )
    return None


def create_user_album_of_the_day_playlist(
    spotify_user: SpotifyUser, database_instance: SavedSpotifyUser
):
    """Each user has a playlist where everything they save end up. This function creates this playlist, with
    additional checks in case the playlist has been deleted.

    :param spotify_user: An object for accessing the Spotify user that should perform the action.

    :param database_instance: A database object that the user's Spotify user is saved in.
    """
    logger.info(
        f"Creating album of the day for playlist for Spotify user {spotify_user.username}..."
    )
    new_playlist = spotify_client.create_playlist(
        user=spotify_user,
        name="🔖 Album of the day: sparat",
        description="Hemsidan Album of the day samlar tankar skrivna om album, ett nytt, varje dag. I denna spellista hamnar den första låten på alla album som har sparats av mig när jag valt att trycka på en knapp för att spara ett album till min Spotify.",
    )
    logger.debug(f"New playlist data: {new_playlist}")
    logger.info(
        f"New playlist created for Spotify user {spotify_user.username}. Saving in database..."
    )
    database_instance.connected_playlist_id = new_playlist["id"]
    database_instance.save()
    logger.info("Database updated with new playlist.")
    return new_playlist  # Return the new playlist


def get_user_album_of_the_day_playlist(
    spotify_user: SpotifyUser, database_instance: SavedSpotifyUser
):
    """Each user has a playlist where everything they save end up. This function retrieves this playlist, with
    additional checks in case the playlist has been deleted.

    :param spotify_user: An object for accessing the Spotify user that should perform the action.

    :param database_instance: A database object that the user's Spotify user is saved in.

    """
    logger.info(f"Checking for playlist for Spotify user {spotify_user.username}...")
    try:
        playlist_data = spotify_client.get_user_playlist(
            spotify_user, database_instance.connected_playlist_id
        )
        logger.info(
            f"Succeeded to retrieve connected playlist data for {spotify_user.username} ({playlist_data})."
        )
        return playlist_data
    except Exception as e:
        logger.warning(
            f"Failed to retrieve playlist for Spotify user {spotify_user.username}. The following error occurred: {e}",
            exc_info=True,
        )
        # Here, we create a new playlist
        logger.info("Creating a new playlist for the user...")
        return create_user_album_of_the_day_playlist(spotify_user, database_instance)


def on_updated_tokens(spotify_user: SpotifyUser):
    """Callback function that we can pass to the Spotify API Client so that it can inform us
    when the tokens have been updated. This allows the database to keep a consistent copy of the
    tokens that are in use.

    :param spotify_user: The Spotify user with the correct tokens."""
    logger.info("Updating Spotify tokens for saved Spotify user...")
    saved_spotify_user = SavedSpotifyUser.objects.filter(
        id=spotify_user.linked_database_id
    ).first()  # Note: I do not catch the None case because it should not be expected.
    saved_spotify_user.token_expires_at = spotify_user.expires_datetime
    saved_spotify_user.access_token = spotify_user.access_token
    logger.info("Access tokens have been updated in memory. Updating database...")
    saved_spotify_user.save()
    logger.info("Spotify user has been updated in database. Tokens have been saved.")


def get_spotify_user_from_saved(database_instance: SavedSpotifyUser):
    """Creates a SpotifyUser (for use with the API client) from a saved Spotify user (SavedSpotifyUser).

    :param database_instance:  A database object that the user's Spotify user is saved in.
    """
    token_expires_in_seconds = round(
        (
            datetime.datetime.now().astimezone(pytz.UTC)
            - database_instance.token_expires_at.astimezone(pytz.UTC)
        ).total_seconds()
    )
    return SpotifyUser(
        access_token=database_instance.access_token,
        client_id=spotify_client.client_id,
        refresh_token=database_instance.refresh_token,
        expires_in=token_expires_in_seconds,
        authorization_header=spotify_client.authorization_header,
        user_agent=spotify_client.user_agent,
        on_token_refresh=on_updated_tokens,
        linked_database_id=database_instance.id,
    )


def get_playlist_items(
    spotify_user: SpotifyUser,
    database_instance: SavedSpotifyUser,
    playlist_id: str,
    recalled_times: Optional[int] = None,
) -> Tuple[List[Dict], List[str]]:
    """Gets all playlist items for a certain playlist. Also parses and returns all UIDs in it (thus I created a new function)

    :param spotify_user: The Spotify user to authenticate with.

    :param database_instance:  A database object that the user's Spotify user is saved in.

    :param playlist_id: The playlist ID to retrieve.

    :param recalled_times: Used for recursion to avoid spamming spotify.

    :returns A tuple in the format of (<playlist items (raw return from API client function), playlist items UIDs>
    """
    if recalled_times is None:
        recalled_times = 0
    try:
        playlist_items = spotify_client.get_user_playlist_items(
            spotify_user, playlist_id
        )
    except SpotifyDataNotFound:
        # This was interesting. The Spotify API did not give 404 when I tried to retrieve a deleted playlist!
        # In fact, it even gave me the playlist data...
        # But when I got to this state, I got a 404. So here, we handle that case that the user deleted the playlist
        # in case Spotify's API does not catch it earlier.
        logger.warning(
            f"Seems like {spotify_user.username} deleted their playlist (handled by track list)."
        )
        if recalled_times < 3:
            logger.info("Creating a new one...")
            new_playlist = create_user_album_of_the_day_playlist(
                spotify_user, database_instance
            )
            return get_playlist_items(
                spotify_user=spotify_user,
                database_instance=database_instance,
                playlist_id=new_playlist["id"],
                recalled_times=recalled_times + 1,
            )
        else:
            raise SpotifyAPIException(
                "Failed to create a Spotify playlist multiple times."
            )
    playlist_items_uris = [
        playlist_item["track"]["uri"] for playlist_item in playlist_items
    ]  # Create a list of all URIs
    return playlist_items, playlist_items_uris


# Views related to Spotify saving
# NOTE: errors are handled by the frontend, which has a URL that receives an error parameter
# with a type which is one of SpotifyAuthenticationErrors. The URL is set below
FRONTEND_SPOTIFY_STATUS_URL = f"{os.environ['FRONTEND_BASE_URL']}/spotify-callback"


class SpotifyAuthenticationErrors(Enum):
    STATE_MISMATCH = "state_mismatch"  # There is a mismatch between the state requested and the state received
    SPOTIFY_ERROR = "spotify_error"
    MISSING_PERMISSIONS = (
        "missing_permissions"  # If the user did not gave appropriate permissions
    )


spotify_client = SpotifyClient(
    os.environ["SPOTIFY_CLIENT_ID"],
    os.environ["SPOTIFY_CLIENT_SECRET"],
    os.environ["SPOTIFY_USER_AGENT"],
)  # Create a Spotify client
SPOTIFY_REDIRECT_URL = f"{os.environ['BASE_URL']}/spotify/callback"


class GetSpotifyAuthenticationStatusView(views.APIView):
    """Returns the user's authentication status with Spotify. It exposes
    an API endpoint that can be requested by the frontend to ensure that it has the correct authentication status
    (for example, if the cookie to store the user's token exists but the database has been wiped and the token has changed,
    the frontend has no idea that it has.)"""

    schema = None  # Do not include this endpoint in the documentation

    def get(self, request, format=None):
        logger.info("Got a request to get Spotify authentication status...")
        if "spotify_token" not in request.GET:
            logger.info("Missing Spotify token in request. Returning error...")
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": "No token to check provided. You have to provide it in the ?spotify_url parameter.",
                }
            )
        saved_spotify_profile = get_saved_spotify_profile_from_request(
            request, source="url"
        )
        authenticated = saved_spotify_profile is not None
        logger.info("Data retrieved. Returning response...")
        return Response(
            {
                "authenticated": authenticated,
                "username": None
                if not authenticated
                else saved_spotify_profile.spotify_username,
                "user_id": None
                if not authenticated
                else saved_spotify_profile.spotify_user_id,
            }
        )


def spotify_authentication_view(request):
    """Handles the first step to user authentication with Spotify:
    redirecting to a URL where the user can authenticate."""
    logger.info("Got a request to authenticate with Spotify.")
    # Check that authentication can be done
    saved_spotify_profile = get_saved_spotify_profile_from_request(
        request, source="url"
    )
    if saved_spotify_profile is not None:
        logger.info("User is already authenticated. Redirecting to frontend...")
        return redirect(
            f"{FRONTEND_SPOTIFY_STATUS_URL}?status=success&username={saved_spotify_profile.spotify_username}&token={saved_spotify_profile.cookie_token}"
        )  # The frontend has an status page for Spotify auth that we are using.
    logger.info("Requesting authentication: generating redirect URL...")
    state = get_random_string(
        8
    )  # Spotify API recommends we use a state to prevent against CSRF. Let's do that!
    redirect_url = spotify_client.generate_user_authentication_url(
        SPOTIFY_REDIRECT_URL,
        state=state,
        scopes=[
            SpotifyScope.MODIFY_PUBLIC_PLAYLIST,
            SpotifyScope.MODIFY_PRIVATE_PLAYLIST,
            SpotifyScope.READ_PRIVATE_PLAYLIST,
            SpotifyScope.READ_COLLABORATE_PLAYLIST,
        ],  # Request access to playlist data
    )
    response = redirect(redirect_url)
    in_one_year = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("spotify_state", state, expires=in_one_year)  # Save the state
    return response


def spotify_callback_view(request):
    """Handles redirects from Spotify authentication and sets and saves a user in the database."""
    logger.info(
        f"Handling a callback redirect from Spotify with parameters: {request.GET}"
    )
    # Get the state from the user's cookies
    state = request.COOKIES.get("spotify_state", None)
    if state is None:
        logger.critical(
            f"No state cookie set (cookie keys: {request.COOKIES.keys()}). Aborting authorization..."
        )
        return redirect(
            f"{FRONTEND_SPOTIFY_STATUS_URL}?status=error&type={SpotifyAuthenticationErrors.STATE_MISMATCH.value}"
        )  # The frontend has an error page for Spotify auth.
    if "error" in request.GET:
        logger.critical(f"Spotify error occurred: {request.GET['error']}.")
        if request.GET["error"] != "access_denied":
            return redirect(
                f"{FRONTEND_SPOTIFY_STATUS_URL}?status=error&type={SpotifyAuthenticationErrors.SPOTIFY_ERROR.value}&error_id={request.GET['error']}"
            )
        else:
            return redirect(
                f"{FRONTEND_SPOTIFY_STATUS_URL}?status=error&type={SpotifyAuthenticationErrors.MISSING_PERMISSIONS.value}"
            )
    spotify_user = spotify_client.get_user_from_redirect(
        redirect_uri=SPOTIFY_REDIRECT_URL, response_parameters=request.GET
    )
    # Check if user previously exists
    previous_spotify_user = SavedSpotifyUser.objects.filter(
        spotify_user_id=spotify_user.id
    ).first()
    if previous_spotify_user:
        logger.info("A previous Spotify user already exists.")
        cookie_token = previous_spotify_user.cookie_token
        user = previous_spotify_user
    else:
        logger.info("Creating a new Spotify user entry for this user...")
        cookie_token = get_random_string(
            16
        )  # Generate a random token to store in cookies to connect to this user
        user = SavedSpotifyUser(
            cookie_token=cookie_token,
            access_token=spotify_user.access_token,
            refresh_token=spotify_user.refresh_token,
            token_expires_at=spotify_user.expires_datetime,
            spotify_username=spotify_user.username,
            spotify_user_id=spotify_user.id,
        )
        user.save()
        logger.info("Saved Spotify user in database.")
    logger.info("Ensuring a playlist has been created...")
    get_user_album_of_the_day_playlist(
        spotify_user, user
    )  # (retrieving the "Album of the day" playlist will create a new one if it fails
    logger.info("Setting cookie and returning response...")
    response = redirect(
        f"{FRONTEND_SPOTIFY_STATUS_URL}?status=success&username={spotify_user.username}&token={cookie_token}"
    )
    in_one_year = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("spotify_token", cookie_token, expires=in_one_year)
    return response


class ToggleAlbumStatusInSpotifyView(generics.CreateAPIView):
    """Endpoint for adding or removing an album to a user's linked Album of the day Spotify playlist.
    This action will be determined automatically.
    Usage: Pass a URL parameter called ?items with Spotify URIs to add to playlist inside of it.
    Multiple items can be added with a comma-delimiter between each."""

    permission_classes = [permissions.AllowAny]
    schema = None  # Do not include this endpoint in the documentation

    def post(self, request):
        logger.info("Got a request to add an album to a user's linked playlist.")
        # Validate parameters
        items_raw = request.GET.get("items", None)
        spotify_token = request.GET.get("spotify_token", None)
        if spotify_token is None:
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": '"spotify_token" key not present in the request.',
                }
            )
        if items_raw is None:
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": '"items" key not present in the request.',
                }
            )
        user = get_saved_spotify_profile_from_request(request, source="url")
        if user is None:  # Ensure a user was found
            logger.info("Did not find a linked user. Returning error...")
            raise NotFoundException(
                detail={
                    "status": "error",
                    "message": "Did not find a linked Spotify user. Please reload the page and try again.",
                }
            )
        items = items_raw.split(",")
        if len(items) == 0:  # Ensure the request included items to add
            logger.warning(
                f"The items key did not contain any items to add: {items}, raw: {items_raw}"
            )
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": "No items to add. Please check the items key.",
                }
            )
        spotify_user = get_spotify_user_from_saved(user)
        linked_playlist = get_user_album_of_the_day_playlist(spotify_user, user)
        linked_playlist_id = linked_playlist["id"]
        linked_playlist_items, linked_playlist_items_uris = get_playlist_items(
            spotify_user, user, linked_playlist_id
        )
        # For each URI, check if the item is already in the playlist.
        # If it is, remove it
        items_to_add = []
        items_to_remove = []
        for item in items:
            if item in linked_playlist_items_uris:
                logger.debug(f"Detected an item to remove: {item}")
                items_to_remove.append(item)
            else:
                logger.debug(f"Detected an item to add: {item}.")
                items_to_add.append(item)
        logger.info(
            f"Found {len(items_to_add)} items to add to the playlist, and {len(items_to_remove)} items to remove."
        )
        if len(items_to_add) > 0:
            # Perform request
            logger.info("Sending request to Spotify to add items...")
            try:
                response_json = spotify_client.add_items_to_playlist(
                    user=spotify_user,
                    playlist_id=linked_playlist_id,
                    uris_to_insert=items_to_add,
                )
                logger.info("Request to add items sent.")
            except Exception as e:
                logger.critical(
                    f"Failed to add items from Spotify playlist! The request failed with the exception {e}. Returning error...",
                    exc_info=True,
                )
                raise InternalServerErrorException(
                    {
                        "status": "error",
                        "message": "The request to Spotify to add playlist items failed.",
                    }
                )
        else:
            logger.info("No items to add.  No request will be sent.")
        if len(items_to_remove) > 0:
            # Perform request
            logger.info("Sending request to Spotify to remove items...")
            try:
                response_json = spotify_client.remove_items_from_playlist(
                    user=spotify_user,
                    playlist_id=linked_playlist_id,
                    uris_to_remove=items_to_remove,
                )
                logger.info("Request to remove items sent.")
            except Exception as e:
                logger.critical(
                    f"Failed to remove items from Spotify playlist! The request failed with the exception {e}. Returning error...",
                    exc_info=True,
                )
                raise InternalServerErrorException(
                    {
                        "status": "error",
                        "message": "The request to Spotify to remove playlist items failed.",
                    }
                )
        else:
            logger.info("No items to remove. No request will be sent.")
        logger.info(
            "Request sent and the item(s) were added or removed. Returning ok..."
        )
        return Response(
            {
                "status": "success",
                "message": "Items were added/removed.",
                "number_of_removed_items": len(items_to_remove),
                "number_of_added_items": len(items_to_add),
            }
        )


class AlbumAddedToSpotifyResponses(Enum):
    linked_user_not_found = "linked_user_not_found"
    no_spotify_user_token_provided = "no_spotify_user_token_provided"
    # (this is the cookie token, not the actual Spotify token. See the model for more information)
    no_album_id_provided = "no_album_id_provided"
    album_id_not_a_number = "album_id_is_nan"
    requested_album_not_found = "album_not_found"
    spotify_uid_not_available = "no_spotify_uid"
    spotify_track_uris_not_available = (
        "spotify_track_uris_not_available"  # (this is a kind of internal server error)
    )


class GetAlbumAddedToSpotifyView(views.APIView):
    """Checks if an album has been added to a user's linked Spotify playlist.
    Returns a response that includes such details. Usage: include ?album_id as a URL parameter
    where the album_id is the ID that an album has in the database."""

    schema = None  # Do not include this endpoint in the documentation

    def get(self, request, *args, **kwargs):
        logger.info(
            "Got a response to check if an album is added to Spotify playlist. Validating parameters"
        )
        # Validate parameters
        # Check if the album ID and user token URL parameter exists.
        spotify_token = request.GET.get("spotify_token", None)
        if spotify_token is None:
            logger.info("User did not pass a Spotify token. Returning error...")
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": "You did not provide an Spotify token in your request.",
                    "type": AlbumAddedToSpotifyResponses.no_spotify_user_token_provided.value,
                }
            )
        album_id = request.GET.get("album_id", None)
        if album_id is None:
            logger.info("User did not pass an album ID. Returning error...")
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": "You did not provide an album ID in your request.",
                    "type": AlbumAddedToSpotifyResponses.no_album_id_provided.value,
                }
            )
        try:  # Ensure that the album_id is valid.
            album_id = int(album_id)
        except Exception as e:
            logger.info("Invalid album ID. Returning error...")
            raise BadRequestException(
                detail={
                    "status": "error",
                    "message": "The provided album ID is not a valid integer.",
                    "type": AlbumAddedToSpotifyResponses.album_id_not_a_number.value,
                }
            )
        user = get_saved_spotify_profile_from_request(request, source="url")
        if user is None:
            logger.info("Did not find a linked user. Returning error...")
            raise NotFoundException(
                detail={
                    "status": "error",
                    "message": "Did not find a linked Spotify user. Please reload the page and try again.",
                    "type": AlbumAddedToSpotifyResponses.spotify_uid_not_available.value,
                }
            )

        album = Album.objects.filter(id=album_id).first()
        if album is None:  # Check that the album was found
            logger.info(f"Did not find a album for ID {album_id}. Returning error...")
            raise NotFoundException(
                detail={
                    "status": "error",
                    "message": f"Did not find a linked album for album {album_id}.",
                    "type": AlbumAddedToSpotifyResponses.requested_album_not_found.value,
                }
            )
        if (
            album.spotify_uid is None or len(album.spotify_uid) == 0
        ):  # Check that the album has a Spotify UID set
            logger.info(f"No Spotify UID for album {album}. Returning error...")
            raise NotFoundException(
                detail={
                    "status": "error",
                    "message": f"Did not find a linked Spotify album for album {album_id}.",
                    "type": AlbumAddedToSpotifyResponses.spotify_uid_not_available.value,
                }
            )
        try:
            spotify_track_uris = json.loads(album.spotify_track_uris)
        except Exception as e:
            logger.critical(
                f"Failed to descerialize track URI json for album {album_id}: the exception {e} occurred.",
                exc_info=True,
            )
            raise InternalServerErrorException(
                detail={
                    "status": "error",
                    "message": f"Failed to load track URIs for album {album_id}.",
                    "type": AlbumAddedToSpotifyResponses.spotify_track_uris_not_available.value,
                }
            )
        spotify_user = get_spotify_user_from_saved(user)
        linked_playlist_id = get_user_album_of_the_day_playlist(spotify_user, user)[
            "id"
        ]
        linked_playlist_items, linked_playlist_items_uris = get_playlist_items(
            spotify_user, user, linked_playlist_id
        )
        return Response(
            {
                "status": "success",
                "is_added_to_playlist": any(
                    [
                        track_uri in linked_playlist_items_uris
                        for track_uri in spotify_track_uris
                    ]
                ),
                "spotify_uid": album.spotify_uid,
            }
        )
