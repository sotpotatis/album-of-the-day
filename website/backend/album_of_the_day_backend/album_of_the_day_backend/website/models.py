import json
import random
import warnings, sys
import time
from threading import Thread

from spotify_api_client.client import (
    SpotifyClient,
    SpotifyUser,
    SpotifyScope,
    SpotifyAPIException,
    SpotifyDataNotFound,
    ClientCredentials,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers
import logging, os
from last_fm_api_client.client import Client, LastFMDataNotFound
from typing import Tuple, Union, Optional
from collections import OrderedDict

# Create logger
logger = logging.getLogger(__name__)

# Load constants
SPOTIFY_MARKET = os.environ.get("SPOTIFY_MARKET", "SE")


# Define all models
class Artist(models.Model):
    """An artist refers to a musical artist or group, for example Pavement, Jenny Hval etc. etc."""

    id = models.AutoField(primary_key=True, help_text="A unique ID of the artist.")
    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        help_text='The name of the artist, e.g. "Pavement."',
    )

    def __str__(self):
        return f'Artist "{self.name}"'


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = "__all__"


GENRE_TAILWIND_COLOR_NUMBER = 600  # Number to use for Tailwind colors for genres
TAILWIND_COLOR_NAMES = [  # List of all Tailwind color names
    "Slate",
    "Gray",
    "Zinc",
    "Neutral",
    "Stone",
    "Red",
    "Orange",
    "Amber",
    "Yellow",
    "Lime",
    "Green",
    "Emerald",
    "Teal",
    "Cyan",
    "Sky",
    "Blue",
    "Indigo",
    "Violet",
    "Purple",
    "Pink",
    "Rose",
]


class Genre(models.Model):
    """A genre refers to a musical genre. For example indie rock, post-rock, ambient, etc."""

    id = models.AutoField(primary_key=True, help_text="An ID of the genre.")
    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        help_text='The name of the genre, e.g. "avant-folk".',
    )
    description = models.CharField(
        max_length=10000,
        null=True,
        blank=True,
        default=None,
        help_text="A description of the genre.",
    )
    description_source = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text="Where the description was sourced from. An ID.",
    )
    # Note: if you would like to know why I did not add a Last.FM genre/tag link as a model attribute, read the comments inside GenreHeader.svelte
    # in the frontend source code.
    color = models.CharField(
        max_length=32,
        help_text="A Tailwind color that can be used to represent the genre in.",
        default=f"gray-{GENRE_TAILWIND_COLOR_NUMBER}",
    )

    # On create, generate a Tailwind color for the model.
    def __str__(self):
        return f'Genre "{self.name}"'


@receiver(post_save, sender=Genre)
def create_tailwind_color_for_genre_on_save(
    sender, instance, created, raw, using, update_fields, **kwargs
):
    """Automatically add a Tailwind color for genres once they have been created.
    Note: for more information on the parameters, please refer to the Django documentation:
    https://docs.djangoproject.com/en/4.2/ref/signals/#post-save
    """
    if created and (update_fields is None or "color" not in update_fields):
        logger.info(f"Picking Tailwind color for genre {instance}...")
        instance.color = f"{random.choice(TAILWIND_COLOR_NAMES).lower()}-{GENRE_TAILWIND_COLOR_NUMBER}"
        logger.info(f"Color picked: {instance.color} Updating...")
        instance.save()
        logger.info("Updated color saved in database.")


class GenreSerializer(serializers.ModelSerializer):
    # Add a custom field, "albums", that counts the current number
    # of albums in the genre
    album_count = serializers.SerializerMethodField()

    def get_album_count(self, instance):
        """Custom field that returns the number of albums in the genre."""
        return Album.objects.filter(genres__in=[instance]).count()

    class Meta:
        model = Genre
        fields = "__all__"


class Album(models.Model):
    """An album refers to a published musical album."""

    id = models.AutoField(primary_key=True, help_text="An individual ID of the album.")
    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        help_text='The name of the album, e.g. "Clarity"',
    )
    artists = models.ManyToManyField(
        Artist,
        related_name="album_artists",
        help_text="The artists that created this album.",
    )
    genres = models.ManyToManyField(
        Genre, related_name="album_genres", help_text="The genres that this album is."
    )
    cover_url = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        default=None,
        help_text="A link to the album cover.",
    )
    cover_source = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        default=None,
        help_text="Where the cover was sourced from. And ID.",
    )
    spotify_uid = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        default=None,
        help_text="""
    A Spotify UID that is associated with the album. Used for the \"\save to Spotify\" feature.""",
    )
    spotify_track_uris = models.CharField(
        max_length=5000,
        default="[]",
        blank=True,
        help_text="""A list of Spotify URIs for all tracks on the album. Used for the \"\save to Spotify\" feature.""",
    )

    def __str__(self):
        return f'Album "{self.name}"'


# List of external fields on Album. Used for prefetch queries
ALBUM_RELATED_FIELDS = ["artists", "genres"]


def retrieve_and_update_cover_url_for_instance(instance: Album):
    """Retrieves and updates the cover URL for an album instance. Retrieves data from Last.FM.

    :param instance: The instance (actual object) to retrieve and update the cover for.
    """
    logger.info(f"Looking for a cover URL for {instance.name}...")
    wait_until_artists(instance)
    # Initialize a Last.FM API client
    client = Client(os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_USER_AGENT"])
    try:
        logger.info("Sending request to Last.FM for album details...")
        # Use the first artist's name as the artist name
        artist_name = instance.artists.first().name
        album_data = client.get_album(album=instance.name, artist=artist_name)
        logger.info("Got album data response. Checking images...")
        if len(album_data.album.image) > 0:
            logger.info(
                f"Found image cover URL(s) for album {instance.name}! Checking..."
            )
            # Double-check that the image URL isn't empty
            # Start from the end, since it is where the biggest images are.
            for i in range(len(album_data.album.image) - 1, 0, -1):
                album_image = album_data.album.image[i]
                if album_image.url is not None and len(album_image.url) > 0:
                    if instance.cover_url != album_image.url:
                        logger.info(f"Using cover URL of size {album_image.size}.")
                        instance.cover_url = album_image.url
                        instance.cover_source = "last_fm"  # Static for now since we only use Last.FM for the source
                        logger.info(f"Saving new cover for album {instance.name}...")
                        instance.save()
                        logger.info(f"Cover for album {instance.name} was saved.")
                        break
                    else:
                        logger.info(
                            f"Will not update cover for album {instance.name}: Is already the same as in the API."
                        )
                        break
                else:
                    logger.warning(
                        f"Will not use album cover size {album_image.size} - URL is empty or None ({album_image.url}."
                    )
            # Since we check for empty images, throw a warning if all images were empty (highly unlikely but possible)
            if instance.cover_url is None:
                logger.warning(
                    f"Did not find any images for album {instance.name} (all sizes were empty). Its cover will be left blank."
                )
        else:
            logger.warning(
                f"Did not find any images for album {instance.name}. Its cover will be left blank."
            )
    except LastFMDataNotFound as e:
        logger.warning(
            f"Failed to retrieve a cover URL for album {instance.name} (was not found). Its cover will be left blank.",
            exc_info=True,
        )
    except Exception as e:
        logger.warning(
            f"Failed to retrieve a cover URL for album {instance.name} (unhandled exception: {e}). Its cover will be left blank.",
            exc_info=True,
        )


def retrieve_and_update_spotify_uid_for_instance(instance: Album):
    """Retrieves and updates the Spotify UID for an album by searching for it on Spotify.

    :param instance: The album instance to look for UIDs for."""
    logger.info(f"Trying to find a Spotify UID for album {instance.name}...")
    wait_until_artists(instance)
    # Initialize a Spotify client
    spotify_client = SpotifyClient(
        os.environ["SPOTIFY_CLIENT_ID"],
        os.environ["SPOTIFY_CLIENT_SECRET"],
        os.environ["SPOTIFY_USER_AGENT"],
    )
    # ...and some client credentials
    client_credentials = ClientCredentials(
        spotify_client.authorization_header, spotify_client.user_agent
    )
    try:
        # Use the first artist's name as the artist name
        artist_name = instance.artists.first().name
        logger.info("Sending request to Spotify...")
        # When searching, we only want the first album. The market can be customized but defaults to Swedish.
        search_results = spotify_client.search(
            client_credentials=client_credentials,
            query=f"album:{instance.name} artist:{artist_name}",
            type="album",  # Only return albums...
            market=SPOTIFY_MARKET,  # ...available in our requested market
            limit=1,
        )
        logger.info("Got search results back. Handling...")
        album = search_results[0]
        album_id = album["id"]
        logger.info(f"Found Spotify UID: {album_id}. Getting ID for tracks...")
        # We save the IDs for all tracks as well so we can add tracks to the user's stored Album of the day playlist via an API.
        # See views.py or play around with the frontend.
        album_tracks = spotify_client.get_album_tracklist(
            credentials=client_credentials, album_uid=album_id, market=SPOTIFY_MARKET
        )
        track_uris = [track["uri"] for track in album_tracks]
        instance.spotify_uid = album_id
        if len(track_uris) == 0:
            logger.warning(
                f"Missing track URIs for album with UID {album_id} - we have a length of 0 track URIs!"
            )
        instance.spotify_track_uris = json.dumps(track_uris)
        instance.save()
        logger.info(f"Spotify UID for {instance.name} was saved.")
    except SpotifyDataNotFound as e:
        logger.warning(
            f"Failed to find a Spotify UID for album {instance.name} (was not found). Its UID will be left blank.",
            exc_info=True,
        )
    except Exception as e:
        logger.warning(
            f"Failed to find a Spotify UID for album {instance.name} (unhandled exception: {e}). Its UID will be left blank."
        )


def wait_until_artists(instance: Album, timeout: Optional[int] = None) -> None:
    """When an album is created and received by the post_save hooks below,
    it still doesn't have artists because its ManyToMany relationship requires
    the album to exist before artists can be added (post_save is run before artists
    are added). This function waits until an Album has .artists != None.

    :param instance: The instance of the album to check.

    :param timeout: An optional timeout. Default is 30 seconds."""
    if timeout is None:
        timeout = 30
    if instance.artists.first() is None:
        time_elapsed = 0
        # Run until timeout or until we have artists
        while time_elapsed < timeout and instance.artists.first() is None:
            # Print out debugging every 2 seconds
            if time_elapsed % 2 == 0:
                logger.info(
                    f"Waiting until artists are created on {instance} ({time_elapsed}s elapsed)..."
                )
            time.sleep(1)
            time_elapsed += 1
        # Raise a TimeoutError if we do not get artists added
        if instance.artists.first() is None:
            error_message = (
                f"Timeout exceeded waiting for artists to be created on {instance}."
            )
            logger.warning(error_message)
            raise TimeoutError(error_message)


@receiver(post_save, sender=Album)
def retrieve_cover_url_for_album_on_save(
    sender, instance, created, raw, using, update_fields, **kwargs
):
    """Automatically retrieve cover URL when an album is or created to ensure that it is up to date.

    Note: for more information on the parameters, please refer to the Django documentation:
    https://docs.djangoproject.com/en/4.2/ref/signals/#post-save

    Note: automatic updating of cover URLs is done using the task update_album_cover.
    """
    # Only run when an album is created and the field has not been manually set
    if created and (update_fields is None or "cover_url" not in update_fields):
        # Create a thread to queue the retrieval
        thread = Thread(
            target=retrieve_and_update_cover_url_for_instance, args=[instance]
        )
        thread.start()
    else:
        logger.info(
            "Ignored retrieving cover for an album: it has already been created."
        )


@receiver(post_save, sender=Album)
def retrieve_uid_for_album_on_save(
    sender, instance, created, raw, using, update_fields, **kwargs
):
    """Automatically retrieve Spotify UUID when an album is or created to ensure that it is up to date.

    Note: for more information on the parameters, please refer to the Django documentation:
    https://docs.djangoproject.com/en/4.2/ref/signals/#post-save

    Note: automatic updating of Spotify UIDs is done using the task update_spotify_uids.
    """
    # Only run when an album is created and the field has not been manually set
    if created and (update_fields is None or "update_uids" not in update_fields):
        # Create a thread to queue the retrieval
        thread = Thread(
            target=retrieve_and_update_spotify_uid_for_instance, args=[instance]
        )
        thread.start()
    else:
        logger.info(
            "Ignored retrieving Spotify UIDs for an album: it has already been created."
        )


class AlbumSerializer(serializers.ModelSerializer):
    """Defines a serializer for the AlbumSerializer class."""

    genres = GenreSerializer(many=True)
    artists = ArtistSerializer(many=True)

    class Meta:
        model = Album
        fields = "__all__"

    def to_representation(self, instance):
        """We override the get method of this view to convert spotify_track_uris
        from a JSON string to JSON."""
        spotify_track_uris = []
        try:
            spotify_track_uris = json.loads(instance.spotify_track_uris)
        except Exception as a:  # Since the default value is JSON, this is not expected.
            try:
                spotify_track_uris_value = (
                    f"Track URIs value: {instance.spotify_track_uris}"
                )
            except Exception as b:
                spotify_track_uris_value = f"Track URIs value not available. {str(b)}"
            logger.critical(
                f"Failed to load track URIs value: deserialization failed. This is not expected, please check the spotify_track_uris field of the album {instance.id}. Exception: {str(a)}. {spotify_track_uris_value}",
                exc_info=True,
            )
        return {
            "id": instance.id,
            "name": instance.name,
            "artists": [
                ArtistSerializer(artist).to_representation(artist)
                for artist in instance.artists.all()
            ],
            "genres": [
                GenreSerializer(genre).to_representation(genre)
                for genre in instance.genres.all()
            ],
            "cover_url": instance.cover_url,
            "cover_source": instance.cover_source,
            "spotify_uid": instance.spotify_uid,
            "spotify_track_uris": spotify_track_uris,
        }


class AlbumOfTheDay(models.Model):
    """An AlbumOfTheDay refers to the contents of a daily post about an album.
    Since I have written about one album multiple times without knowing, one album might have multiple
    AlbumOfTheDay entires."""

    id = models.AutoField(primary_key=True, help_text="A unique ID for the album")
    album = models.ForeignKey(
        Album,
        related_name="related_album",
        help_text="The album that the Album of the day post is for.",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        help_text="The day that the album of the day was written on/for."
    )
    comments = models.CharField(
        max_length=10000, null=False, blank=False, help_text="My comments on the album."
    )
    comments_source = models.CharField(
        max_length=128,
        null=False,
        blank=True,
        help_text="""
    The source of the comments (if it was entered from plain text or if it was extracted using OCR, for example). Provide an ID, like \"ocr\" or \"plain_text\".""",
    )


# List of external fields on AlbumOfTheDay. Used for prefetch queries
ALBUM_OF_THE_DAY_RELATED_FIELDS = ["album"]


class AlbumOfTheDaySerializer(serializers.ModelSerializer):
    """Defines a serializer for the AlbumOfTheDay class."""

    class Meta:
        model = AlbumOfTheDay
        ordering = ["date"]
        fields = "__all__"

    def to_representation(self, instance):
        """Override the to_representation method to provide detailed data for the album that is linked to the album of the day entry."""
        return {
            "id": instance.id,
            "comments": instance.comments,
            "comments_source": instance.comments_source,
            "date": instance.date,
            "album": AlbumSerializer(instance.album).to_representation(instance.album),
        }


class AlbumListItem(models.Model):
    """A list item in a album list. The fields here can either be one of the following:
    - Album-related metadata. This contains albums.
    - Text-related metadata. This contains a heading and a body text that can be used to add
    text contents inside the list."""

    # Metadata type 1: album-related.
    album = models.ForeignKey(
        Album,
        blank=True,
        null=True,
        related_name="list_album",
        help_text="An album that is associated with this list item.",
        on_delete=models.CASCADE,
    )
    comments = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text="Any comments about the album that is associated with this list item.",
    )
    # Metadata type 2: text-related
    heading = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="Any heading to include in this list item.",
    )
    body = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="Any body text to include in this list item.",
    )
    # Generic
    index_in_list = models.IntegerField(
        help_text="The index that the item has in the list."
    )

    def __str__(self):
        if self.album is not None:
            return f'Album item "{self.album.name}"'
        else:
            return f"Text item \"{self.heading}\", \"{f'{self.body[:12]}...' if self.body is not None and len(self.body) > 0 else ''}\""


class AlbumListItemSerializer(serializers.ModelSerializer):
    """Defines a serializer for the AlbumListItem class."""

    class Meta:
        model = AlbumListItem
        fields = "__all__"

    def to_representation(self, instance):
        """We override the to_representation() function to allow for two different types of album list items:
        one for album data and one to insert text."""
        filled_out_type = None
        representation = None
        # Check what to include
        if instance.album is not None:  # Album type
            filled_out_type = "album"
            representation = {
                "album": AlbumSerializer(instance.album).to_representation(
                    instance.album
                ),
                "comments": instance.comments,
            }
        elif (instance.heading is not None and len(instance.heading) > 0) or (
            instance.body is not None and len(instance.body) > 0
        ):  # Text type
            filled_out_type = "text"
            representation = {"heading": instance.heading, "body": instance.body}
        else:
            warnings.warn(
                f"Malformatted database item: one AlbumListItem is completely empty."
            )
            return None
        # Add generic keys
        representation["type"] = filled_out_type
        representation["index_in_list"] = instance.index_in_list
        return representation


class AlbumList(models.Model):
    """An AlbumList is a collection of albums that can be created. For example, if you want to collect summer albums or anything else."""

    id = models.AutoField(primary_key=True, help_text="A unique ID for the album list")
    name = models.CharField(
        max_length=256, null=False, blank=False, help_text="The name of the list."
    )
    description = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        help_text="The description of the list.",
    )
    items = models.ManyToManyField(
        AlbumListItem,
        related_name="list_albums",
        help_text="The albums that are in the list.",
    )
    created_at = models.DateTimeField(
        auto_now=True, help_text="When the list was created."
    )

    def __str__(self) -> str:
        return f'Album list "{self.name}" (ID {self.id})'


# List of external fields on AlbumList. Used for prefetch queries
ALBUM_LIST_RELATED_FIELDS = ["items"]


class AlbumListSerializer(serializers.ModelSerializer):
    items = AlbumListItemSerializer(many=True)

    class Meta:
        model = AlbumList
        fields = "__all__"

    def to_representation(self, instance):
        """We override to_representation to sort the items properly. You might think "why not use the filters and sortering that you have
        already installed?" Valid point, but I think it is so crucial that a list appears in the correct order.
        """
        items = [
            AlbumListItemSerializer(item).to_representation(item)
            for item in instance.items.all()  # Format all items
        ]
        items.sort(
            key=lambda item: item["index_in_list"]
        )  # Sort by the "index_in_list" key.
        return {
            "id": instance.id,
            "name": instance.name,
            "description": instance.description,
            "items": items,
            "created_at": instance.created_at.isoformat(),
        }


class DailyRotation(models.Model):
    """A DailyRotation refers to all the albums I have listened to in a particular day."""

    id = models.AutoField(
        primary_key=True, help_text="A unique ID for the daily rotation"
    )
    day = models.DateField(help_text="The day that the rotation is for.")
    description = models.CharField(
        max_length=256,
        null=True,
        help_text='The description/comments of the daily rotation. For example "rainy day, listened to lots of slowcore today..."',
    )
    albums = models.ManyToManyField(
        Album,
        related_name="rotation_albums",
        help_text="The albums that are in the daily rotation.",
    )
    genres = models.ManyToManyField(
        Genre,
        related_name="rotation_genres",
        help_text="The genres that are included in this daily rotation.",
    )


# List of external fields on DailyRotation. Used for prefetch queries.
DAILY_ROTATION_RELATED_FIELDS = ["albums", "genres"]


class DailyRotationSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    albums = AlbumSerializer(many=True)

    class Meta:
        model = DailyRotation
        ordering = ["day"]
        fields = "__all__"


class SavedSpotifyUser(models.Model):
    """A SavedSpotifyUser is a user that has connected their Spotify account to save albums to their profile."""

    id = models.AutoField(primary_key=True, help_text="The ID of the user.")
    cookie_token = models.CharField(
        max_length=128,
        help_text="A token that the user can use for identification purposes.",
    )
    # Spotify is not joking with the size of tokens - tests showed a value of 268, we're alolowing big big space for them.
    access_token = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="The access token for the user's Spotify account.",
    )
    refresh_token = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text="The refresh token for the user's Spotify account.",
    )
    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user token expires, if any token has been retrieved.",
    )
    spotify_username = models.CharField(
        max_length=256, help_text="The user's Spotify username."
    )
    spotify_user_id = models.CharField(
        max_length=256, help_text="The user's Spotify ID."
    )
    connected_playlist_id = models.CharField(
        max_length=256, help_text="The playlist that Album of the Day saves albums to."
    )
