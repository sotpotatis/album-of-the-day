"""create_album_of_the_day.py
Various commands to create an album of the day."""
import asyncio
import os, sys
import tempfile
from asyncio import as_completed
from io import BytesIO, FileIO
import aiohttp
from PIL import Image
from discord.ext.commands import Bot, Cog
from discord.app_commands import command
from discord import Interaction, ButtonStyle, Button, Embed, File
from discord.ui import View, Modal, TextInput, button, Select
from .utilities import (
    get_now,
    generate_error_message,
    generate_loading_message,
    list_to_markdown,
    SUCCESS_EMBED_COLOR,
    INFO_EMBED_COLOR,
    WARNING_EMBED_COLOR,
    ERROR_EMBED_COLOR,
    get_all,
)
from album_image_util.util import create_image
from album_image_util.template_image_data import (
    TEMPLATE_IMAGE_PILLOW,
    ALBUM_COVER_PLACEHOLDER_IMAGE_PILLOW,
)
import logging, django, collections, typing
from asgiref.sync import sync_to_async

django.setup()  # Register Django so we can access models etc.
from website.models import AlbumOfTheDay, Artist, Genre, Album
from website.tasks.util import (
    find_django_artist_from_name,
    find_django_genre_from_name,
    find_django_album_from_details,
    add_album_to_database,
)
from typing import Union, List, Type, Optional
from django.db.models import Model

# Initialize logging
logger = logging.getLogger(__name__)
# Get the font path for album images.
IMAGE_FONT_PATH = os.environ["ALBUM_IMAGES_FONT_PATH"]


# Define different popups: to add a new album, to add a new list, etc.
class AddNewAlbumModal(Modal, title="Lägg till nytt album"):
    album_name = TextInput(
        label="Albumets namn",
        placeholder="t.ex. Joy as an Act of Resistance",
        required=True,
    )
    album_artists = TextInput(label="Artiser", placeholder="t.ex. IDLES", required=True)
    album_genres = TextInput(
        label="Genrer", placeholder="t.ex. avant-folk,post-rock", required=True
    )
    album_comments = TextInput(label="Kommentarer", required=True)
    CONFIRMATION_STATES = ["artists", "genres", "album", "overview"]

    def __init__(
        self,
        is_album_of_the_day: Optional[bool] = None,
        on_done: Optional[typing.Callable] = None,
    ):
        """Creates an AddNewAlbumModal.
        This modal can either be used to create an album of the day, or a new album.
        This can be set with the is_album_of_the_day_parameter.

        :param is_album_of_the_day: Set this to False to create a new album and not a new album of the day. Default is True.

        :param on_done: An optional function to run when the modal is done doing whatever it is doing.
        Will receive the model that has been created - whether it is to create a new album or create a new album of the day.
        """
        # Fill out defaults
        if is_album_of_the_day is None:
            is_album_of_the_day = True
        super().__init__()
        self.is_album_of_the_day = is_album_of_the_day
        # Remove comments if the item is not album of the day
        if not self.is_album_of_the_day:
            self.remove_item(self.album_comments)
        self.on_done = on_done  # Store callback function
        # Define storage for all actions to perform
        self.new_album_artists = {}
        self.old_album_artists = {}
        self.new_album_genres = {}
        self.old_album_genres = {}
        self.album_django = None
        self.datasets = {  # Define where data is changed to when an option is updated for each option
            "new_artists": {
                "source": self.new_album_artists,
                "target": self.old_album_artists,
            },
            "new_genres": {
                "source": self.new_album_genres,
                "target": self.old_album_genres,
            },
            "new_album": {
                "source": {self.album_name: self.album_name},  # Mock data
                "target": {self.album_name: self.album_name},
            },
        }
        self.datasets["old_artists"] = self.datasets["new_artists"]
        self.datasets["old_genres"] = self.datasets["old_artists"]
        self.datasets["old_album"] = self.datasets[
            "new_album"
        ]  # Mirror since we're using mocked data
        # The user will confirm a bunch of stuff after submitting the modal.
        # This list will include "artists", "genres", "album" and "overview"
        # when everything has been confirmed by the user
        self.confirmed = []
        self.things_to_be_confirmed: typing.OrderedDict[
            str, Embed
        ] = (
            collections.OrderedDict()
        )  # Mapping: thing to be confirmed --> embed to send out
        self.current_confirm_state = AddNewAlbumModal.CONFIRMATION_STATES[0]
        self.next_thing_to_be_confirmed = (
            None  # Will be set the first time confirm_next() is called
        )
        self.last_message = None  # Store the last message that was sent by the bot

    class EditView(View):
        """A subview related to the edit actions view that includes select options for customizing the created album of the day."""

        # Create options
        # We have a bunch of different possible options.
        # 1.,2. The user asked to edit the creation of new artists OR the usage of old artists -->
        # ask the user to provide existing items from the database or create a new one
        # 3.,4. The user asked to edit the creation of new genres  OR the usage of old genres-->
        # ask the user to provide existing items from the database or create a new one
        # All of these are handled below, and the dict below defines metadata for each action. Since they are so
        # similar the dict is here to save us lines of code.
        NEW_OPTIONS = {
            "new_artists": {
                "model": Artist,
                "type_name": "artist",
                "embed": {
                    "title": "Välj artister att använda.",
                    "description": "Välj vad du vill göra med respektive albumartist.",
                },
                "fields": {"id": "id", "name": "name"},
            },
            "new_genres": {
                "model": Genre,
                "type_name": "genre",
                "embed": {
                    "title": "Välj genrer att använda.",
                    "description": "Välj vad du vill göra med respektive genre.",
                },
                "fields": {"id": "id", "name": "name"},
            },
            "new_album": {
                "model": Album,
                "type_name": "album",
                "embed": {
                    "title": "Välj album att använda.",
                    "description": "Välj vad du vill göra med albumet.",
                },
                "fields": {"id": "id", "name": "name"},
            },
        }
        # Mirror metadata for the "old" options.
        NEW_OPTIONS["old_artists"] = NEW_OPTIONS["new_artists"]
        NEW_OPTIONS["old_genres"] = NEW_OPTIONS["new_genres"]
        NEW_OPTIONS["old_album"] = NEW_OPTIONS["new_album"]

        def __init__(self, parent_view: "AddNewAlbumModal"):
            """Initializes an EditView.

            :param parent_view: An instance of AddNewAlbumModal that the view is contained in.
            """
            super().__init__()
            self.parent_view = parent_view

        @button(label="Klar", style=ButtonStyle.green)
        async def edits_done(self, interaction: Interaction, button: Button):
            """Callback for the confirmation of the edit changes."""
            await interaction.response.defer()
            logger.info("User confirmed edit changes. Showing next...")
            # Note: we do not have to do anything with the options here: they will already
            # be updated at this stage. See EditActionsSelect for more information.
            await self.parent_view.confirm_next(interaction)

    class ConfirmActionButtons(View):
        """View for confirming or manually editing the addition of an album."""

        def __init__(self, parent_view: "AddNewAlbumModal"):
            """Creates a button set for confirming or manually editing the addition of the album.

            :param parent_view: A link back to the AddNewAlbumModal instance that the buttons derive from.
            """
            super().__init__()
            self.parent_view = parent_view
            # Used for editing flow, see below
            self.filled_out_options = []
            self.number_of_options = None

        @button(label="Ändra", style=ButtonStyle.blurple)
        async def edit_actions(self, interaction: Interaction, button: Button):
            """Allows the user to edit and customize the actions that are performed by the bot."""
            logger.info(
                "Album of the day flow: edit button clicked. Starting edit flow."
            )
            await interaction.response.defer()
            edit_view = AddNewAlbumModal.EditView(self.parent_view)
            # All select view elements have an option to "Add to database"
            # even if its purpose is to allow the user to choose from existing items instead.
            # Why do we have this option? In case there for example are multiple genres to be created and
            # the user only wants one of them to use an existing one.
            # We give some default kwargs for it here to help us
            NEW_ACTION_ADD_TO_DATABASE_OPTION_VALUE = "add_to_database"
            NEW_ACTION_ADD_TO_DATABASE_OPTION_LABEL = "Lägg till som ny"
            NEW_ACTION_ADD_TO_DATABASE_OPTION_DESCRIPTION = (
                "Lägger till som ny i databasen."
            )

            class EditActionsSelect(Select):
                def __init__(
                    self,
                    grandparent_view: "AddNewAlbumModal",
                    parent_view: "AddNewAlbumModal.ConfirmActionButtons",
                    placeholder: str,
                ):
                    """Initializes a select menu for selecting something in the dropdown(s) that will
                    appear when the user customizes what the bot should do.

                    :param grandparent_view: An instance of AddNewAlbumModal that this action menu can access

                    :param parent_view: An instance of AddNewAlbumModal.ConfirmActionButtons that this action menu can access

                    :param placeholder: A placeholder to display in the select."""
                    super().__init__()
                    self.grandparent_view = grandparent_view
                    self.parent_view = parent_view
                    self.placeholder = placeholder

                async def callback(self, interaction: Interaction):
                    """A generic callback for when a user has selected something in the dropdown.
                    Automatically updates whatever that should be updated."""
                    await interaction.response.defer()
                    for option_value in self.values:
                        # Note: the "new" flow is similar for both new_artists and new_genres, so it is automated
                        # using a static definition.
                        logger.info(
                            f"Updating value for {self.grandparent_view.things_to_be_confirmed} for {option_value}..."
                        )
                        action_information = AddNewAlbumModal.EditView.NEW_OPTIONS[
                            self.grandparent_view.next_thing_to_be_confirmed
                        ]
                        action_is_new = (
                            self.grandparent_view.next_thing_to_be_confirmed.startswith(
                                "new"
                            )
                        )
                        # option_value will either be "add_to_database" or the ID of a Django artist.
                        # Unpack the option value, which will be in this format: <item index in Django DB>:<item key in new_artists dict>
                        item_index, original_item_key = option_value.split(":")
                        if item_index != NEW_ACTION_ADD_TO_DATABASE_OPTION_VALUE:
                            item_index = int(item_index)
                            logger.info(
                                f"Getting {action_information['type_name']} from Django database..."
                            )
                            django_item = await sync_to_async(
                                action_information["model"].objects.filter
                            )(id=item_index)
                            django_item = await sync_to_async(django_item.first)()
                            logger.info(
                                f"{action_information['type_name'].capitalize()} retrieved from Django database."
                            )
                            if (
                                "album"
                                not in self.grandparent_view.next_thing_to_be_confirmed
                            ):
                                del self.grandparent_view.datasets[
                                    self.grandparent_view.next_thing_to_be_confirmed
                                ]["source"][
                                    original_item_key
                                ]  # Revoke original action
                                self.grandparent_view.datasets[
                                    self.grandparent_view.next_thing_to_be_confirmed
                                ]["target"][django_item.name] = django_item
                            else:  # The album option is a little different, handle it
                                self.grandparent_view.album_is_new = False
                                self.grandparent_view.album_django = django_item
                                self.grandparent_view.album_name = django_item.name
                        else:
                            # If the option value was to use an old album, make sure we remove it
                            if not action_is_new:
                                logger.info(
                                    "Option is to add as new. Removing old items..."
                                )
                                if (
                                    "album"
                                    not in self.grandparent_view.next_thing_to_be_confirmed
                                ):
                                    del self.grandparent_view.datasets[
                                        self.grandparent_view.next_thing_to_be_confirmed
                                    ]["target"][
                                        original_item_key
                                    ]  # Revoke original action
                                    self.grandparent_view.datasets[
                                        self.grandparent_view.next_thing_to_be_confirmed
                                    ]["source"][original_item_key] = None
                                else:
                                    self.grandparent_view.album_is_new = True
                                    self.grandparent_view.album_django = None
                            else:
                                logger.info(
                                    "Option is to add as new, not doing anything."
                                )

            logger.info("The user requested editing an action.")
            # Get if the action is new (edit if new things should be created) or old (edit if old things should be used)
            action_is_new = self.parent_view.next_thing_to_be_confirmed.startswith(
                "new"
            )
            action_information = AddNewAlbumModal.EditView.NEW_OPTIONS[
                self.parent_view.next_thing_to_be_confirmed
            ]  # Get metadata from the dictionary above
            result_embed = Embed(
                title=action_information["embed"]["title"],
                description=action_information["embed"]["description"],
                color=WARNING_EMBED_COLOR,
            )
            # Add one select for every model instance that the user can change
            for item_name in self.parent_view.datasets[
                self.parent_view.next_thing_to_be_confirmed
            ]["source" if action_is_new else "target"].keys():
                result_embed.add_field(
                    name=f"Val för {item_name}",
                    value=f"Välj vilken {action_information['type_name']} du vill använda från databasen i valen nedan.",
                    inline=True,
                )
                # Get all instances of the model to use and add them so the user can select them
                item_entries_django = await sync_to_async(get_all)(
                    action_information["model"]
                )
                logger.info(
                    f"Fetched {len(item_entries_django)} {action_information['type_name']}(s) from the database."
                )
                item_selection = EditActionsSelect(
                    grandparent_view=self.parent_view,
                    parent_view=self,
                    placeholder=f"Val för {item_name}",
                )
                # Add options for all select entries
                for item_entry_django in item_entries_django:
                    # Get the ID and name. Where to get them from is specified in the options dict above
                    item_entry_django_id = getattr(
                        item_entry_django, action_information["fields"]["id"]
                    )
                    item_entry_django_name = getattr(
                        item_entry_django, action_information["fields"]["name"]
                    )
                    item_selection.add_option(
                        value=f"{item_entry_django_id}:{item_name}",
                        label=item_entry_django_name,
                        description=f"Använder {item_entry_django_name}",
                    )
                    if len(item_selection.options) == 24:  # Split options if needed
                        edit_view.add_item(item=item_selection)
                        item_selection = EditActionsSelect(
                            grandparent_view=self.parent_view,
                            parent_view=self,
                            placeholder=f"Val för {item_name} (forts.)",
                        )
                # Also add option to keep/add the entry as new
                item_selection.add_option(
                    value=f"{NEW_ACTION_ADD_TO_DATABASE_OPTION_VALUE}:{item_name}",
                    label=NEW_ACTION_ADD_TO_DATABASE_OPTION_LABEL,
                    description=NEW_ACTION_ADD_TO_DATABASE_OPTION_DESCRIPTION,
                )
                edit_view.add_item(item=item_selection)
            logger.info(
                f"Sending message to user to confirm the action for {self.parent_view.next_thing_to_be_confirmed}..."
            )
            self.parent_view.last_message = await self.parent_view.last_message.reply(
                embed=result_embed, view=edit_view
            )
            logger.info("Message sent.")
            self.stop()

        @button(label="Godkänn", style=ButtonStyle.green)
        async def confirm_actions(self, interaction: Interaction, button: Button):
            """Confirms the actions suggested by the bot, e.g. adding a set of new artists."""
            logger.info(
                "Album of the day flow: confirm button clicked. Going to the next step..."
            )
            await interaction.response.defer()
            await self.parent_view.confirm_next(interaction)
            self.stop()

    async def confirm_next(self, interaction: Interaction):
        """The user will confirm a bunch of stuff after submitting the modal.
        This function is a helper function to confirm the next thing that is to be confirmed.
        So basically, this is a confirmation/step handling function. It actually does quite a lot for us!
        """
        first_time_running_this = self.next_thing_to_be_confirmed is None
        previously_confirmed = len(
            self.confirmed
        )  # Get how many things that have previously been confirmed
        if previously_confirmed < len(self.things_to_be_confirmed):
            things_to_be_confirmed = list(self.things_to_be_confirmed.keys())
            logger.debug(
                f"Album of the day flow: Things to confirm: {things_to_be_confirmed} (confirmed {previously_confirmed} items so far)"
            )
            thing_to_be_confirmed = things_to_be_confirmed[previously_confirmed]
            if not first_time_running_this:  # If we are not on the first step
                if previously_confirmed + 1 < len(things_to_be_confirmed):
                    self.next_thing_to_be_confirmed = things_to_be_confirmed[
                        previously_confirmed + 1
                    ]
                logger.info(
                    f"Album of the day flow: Confirmed {thing_to_be_confirmed}."
                )
                self.confirmed.append(
                    thing_to_be_confirmed
                )  # Add the next thing to be confirmed
            else:
                self.next_thing_to_be_confirmed = things_to_be_confirmed[0]
            logger.info(
                f"Sending the embed for the next thing to be confirmed ({self.next_thing_to_be_confirmed})..."
            )
            embed_to_send = self.things_to_be_confirmed[self.next_thing_to_be_confirmed]
            buttons = AddNewAlbumModal.ConfirmActionButtons(parent_view=self)
            if first_time_running_this:
                self.last_message = await interaction.followup.send(
                    embed=embed_to_send, view=buttons
                )
            else:
                self.last_message = await self.last_message.reply(
                    embed=embed_to_send, view=buttons
                )
            logger.info("Embed for the next thing has been sent.")
        else:
            # When everything is confirmed
            logger.info(
                "Album of the day flow: Everything is confirmed. Sending out final confirmation..."
            )
            # Create a final confirmation embed
            overview_embed = Embed(
                title="Slutför",
                description="Okej, så här kommer resultatet se ut:",
                color=SUCCESS_EMBED_COLOR,
            )
            overview_embed.add_field(
                name=f"{'➕' if self.album_is_new else '➡️'}Album",
                value=f"{self.album_name}",
                inline=True,
            )
            # Add information to the overview field.
            # The below code adds some fields that include information about any new artists
            # and genres (or if old ones are used).
            # We iterate over a list that defines the title of the embed field
            # as well as the dataset that is attached with it
            for overview_field in [
                {"title": "➕Artister", "entries": self.new_album_artists},
                {"title": "➡️Artister", "entries": self.old_album_artists},
                {"title": "➕Genrer", "entries": self.new_album_genres},
                {"title": "➡️Genrer", "entries": self.old_album_genres},
            ]:
                if (
                    len(overview_field["entries"]) > 0
                ):  # If there is anything inside the current field datasets
                    # Add all keys as a list and as a new field
                    overview_embed.add_field(
                        name=overview_field["title"],
                        value=list_to_markdown(
                            list(overview_field["entries"].keys()),
                            code_ticks_around_items=True,
                        ),
                        inline=False,
                    )
            if self.is_album_of_the_day:
                album_comments = self.album_comments.value
                # Ensure album comments do not take up too much space
                # (maximum 1024 characters is allowed from the Discord API)
                # We do half, because we preview
                if len(album_comments) > 512:
                    # of the comments
                    album_comments = album_comments[:512] + "[...]"
                overview_embed.add_field(
                    name="Kommentarer", value=f"> {album_comments}", inline=True
                )

            class FinalConfirmationButtons(View):
                def __init__(self, parent_view: "AddNewAlbumModal", timeout=180):
                    """Creates a button set for when the album of the day is to be added to the database
                    and one final confirmation is needed.

                    :param parent_view: A link back to the AddNewAlbumModal instance that the button derives from.
                    """
                    super().__init__(timeout=timeout)
                    self.parent_view = parent_view

                @button(label="Avbryt", style=ButtonStyle.red)
                async def on_abort(self, interaction: Interaction, button: Button):
                    """Runs when the user has aborted the addition of the album."""
                    await interaction.response.defer()
                    logger.info(
                        "Action to add album of the day was aborted! Sending out error embed..."
                    )
                    await self.parent_view.last_message.reply(
                        embed=generate_error_message(
                            title="Avbruten",
                            message="""
                                                                                           Okej! Jag kommer inte lägga till albumet. Kör `/add_album_of_the_day` igen för att börja om.""",
                        )
                    )

                @button(label="Godkänn", style=ButtonStyle.green)
                async def on_confirm(self, interaction: Interaction, button: Button):
                    """Runs when the user has clicked the final confirmation to add the album of the day to the database."""
                    await interaction.response.defer()
                    logger.info("Adding album of the day to database...")
                    # Send a loading message
                    self.parent_view.last_message = await self.parent_view.last_message.reply(
                        embed=generate_loading_message(
                            title="Arbetar med databasen...",
                            message="""Jag skapar upp allt som behöver skapas i databasen och ser till att allt ser bra ut... En sekund!""",
                        )
                    )
                    if (
                        self.parent_view.album_is_new
                    ):  # Create a new album if not seen before
                        logger.info("Creating new album...")
                        album = Album(name=self.parent_view.album_name)
                        await sync_to_async(album.save)()
                        logger.info("Album added to database.")
                        # Add genres and artists
                        # First the things to create
                        for new_models, album_field, model_type in [
                            (self.parent_view.new_album_artists, album.artists, Artist),
                            (self.parent_view.new_album_genres, album.genres, Genre),
                        ]:
                            # For each instance to add
                            for new_instance_name in new_models.keys():
                                new_instance = model_type(name=new_instance_name)
                                logger.info(f"Creating {new_instance}...")
                                await sync_to_async(new_instance.save)()
                                logger.info(
                                    f"Created {new_instance}. Adding to album..."
                                )
                                await sync_to_async(album_field.add)(new_instance)
                        # And then the things we already have from the database
                        for old_models, album_field in [
                            (self.parent_view.old_album_artists, album.artists),
                            (self.parent_view.old_album_genres, album.genres),
                        ]:
                            for old_instance, old_instance in old_models.items():
                                logger.info(f"Adding {old_instance} to album...")
                                await sync_to_async(album_field.add)(old_instance)
                                logger.info(f"{old_instance} added to album.")
                        logger.info("Album creation succeeded!")
                    else:
                        logger.info("Using previously defined album.")
                        album = self.parent_view.album_django
                    if self.parent_view.is_album_of_the_day:
                        album_of_the_day = AlbumOfTheDay(
                            album=album,
                            date=get_now().date(),
                            comments=self.parent_view.album_comments.value,
                            comments_source="plain_text",  # Tell that the comments were not OCR:ed etc
                        )
                        logger.info("Adding album of the day to database...")
                        await sync_to_async(album_of_the_day.save)()
                        logger.info(
                            "The album of the day was added to the database. Sending final confirmation message..."
                        )
                        # Create an URL where the new album of the day can be viewed
                        album_of_the_day_url = f"{os.environ['FRONTEND_BASE_URL']}/album-of-the-days/{album_of_the_day.id}"
                        confirmation_embed = Embed(
                            title="✅ Album of the day lades till",
                            description="Jag har lagt till dagens album i databasen.",
                            color=SUCCESS_EMBED_COLOR,
                            url=album_of_the_day_url,
                        )
                        self.created_model = album_of_the_day
                    else:
                        # Create an URL where the new album can be viewed
                        self.created_model = album
                        album_url = (
                            f"{os.environ['FRONTEND_BASE_URL']}/albums/{album.id}"
                        )
                        confirmation_embed = Embed(
                            title="✅ Album lades till",
                            description="Jag har lagt till albumet i databasen.",
                            color=SUCCESS_EMBED_COLOR,
                            url=album_url,
                        )
                    self.parent_view.last_message = await self.parent_view.last_message.edit(  # Edit since the last thing is a loading message
                        embed=confirmation_embed
                    )
                    # Is that all? No, we also generate a little album of the day image to go with the album!
                    # This is so that I for example can show it on the Snapchat story that the album of the day originally
                    # originated from.
                    # (and this only of course is done if the parent thing is creating an album of the day)
                    if self.parent_view.is_album_of_the_day:
                        logger.info("Generating album of the day image(s)...")
                        # Generate artist and genre names
                        album_artist_names = []
                        # Add all artist names, both new and old
                        for album_artist_dataset in [
                            self.parent_view.new_album_artists,
                            self.parent_view.old_album_artists,
                        ]:
                            for album_artist_name in album_artist_dataset.keys():
                                album_artist_names.append(album_artist_name)
                        # Do the same with genres
                        album_genre_names = []
                        for album_genre_dataset in [
                            self.parent_view.new_album_genres,
                            self.parent_view.old_album_genres,
                        ]:
                            for album_genre_name in album_genre_dataset.keys():
                                album_genre_names.append(album_genre_name)
                        self.parent_view.last_message = (
                            image_creating_loading_message
                        ) = await self.parent_view.last_message.reply(
                            embed=generate_loading_message(
                                title="Skapar bild...",
                                message="""Skapar en bild med dagens album som du kan publicera på till exempel en Snapchat-story...
                            Detta kan ta upp till någon minut!""",
                            )
                        )
                        # Finally, we have to include the album cover.
                        # This cover will be downloaded from online if it is available.
                        logger.info(
                            "Re-retrieving album of the day in 5 seconds, hoping for an album image!"
                        )
                        await asyncio.sleep(5)
                        logger.info("Re-retrieving album of the day...")
                        album_of_the_day = await sync_to_async(
                            AlbumOfTheDay.objects.filter
                        )(id=album_of_the_day.id)
                        album_of_the_day = await sync_to_async(album_of_the_day.first)()
                        album_of_the_day_related_album = await sync_to_async(getattr)(
                            album_of_the_day, "album"
                        )
                        if (
                            album_of_the_day_related_album.cover_url is not None
                            and len(album_of_the_day_related_album.cover_url) > 0
                        ):
                            logger.info("Cover URL is available. Retrieving...")
                            async with aiohttp.ClientSession() as session:
                                async with session.get(
                                    album_of_the_day_related_album.cover_url
                                ) as response:
                                    if response.status == 200:
                                        logger.info(
                                            "Succeeded to retrieve cover URL! Reading data..."
                                        )
                                        album_cover_image_data = await response.read()
                                        album_cover_image = Image.open(
                                            BytesIO(album_cover_image_data)
                                        )
                                        logger.info("Album cover image retrieved.")
                                    else:
                                        logger.warning(
                                            f"Failed to retrieve cover URL: status code {response.status}"
                                        )
                        else:
                            logger.info(
                                "No album cover URL is available. Using placeholder..."
                            )
                            album_cover_image = ALBUM_COVER_PLACEHOLDER_IMAGE_PILLOW
                        logger.info("Starting creation of album of the day images...")
                        album_of_the_day_images = create_image(
                            input_image=TEMPLATE_IMAGE_PILLOW,
                            album_name=album.name,
                            artist_name=album_artist_names,
                            genre_names=album_genre_names,
                            comments=album_of_the_day.comments,
                            font_path=IMAGE_FONT_PATH,
                            album_cover=album_cover_image,
                        )
                        logger.info(
                            "Album of the day image(s) created. Sending them..."
                        )
                        for i in range(len(album_of_the_day_images)):
                            album_of_the_day_image = album_of_the_day_images[i]
                            # To get the data from the image, we save it into memory
                            album_of_the_day_image_bytes = BytesIO()
                            album_of_the_day_image.save(
                                album_of_the_day_image_bytes, format="PNG"
                            )
                            album_of_the_day_image_bytes.seek(0)
                            self.parent_view.last_message = (
                                await self.parent_view.last_message.reply(
                                    file=File(
                                        album_of_the_day_image_bytes,
                                        f"album_of_the_day-{i}.png",
                                    )
                                )
                            )
                        logger.info(
                            "All album of the day images have been sent in the channel."
                        )
                        await image_creating_loading_message.delete()
                    if self.parent_view.on_done is not None:
                        logger.info('Running callback function, "on_done" function...')
                        await self.parent_view.on_done(self.created_model)
                        logger.info("Callback function ran.")

            await self.last_message.reply(
                embed=overview_embed, view=FinalConfirmationButtons(parent_view=self)
            )

    async def on_submit(self, interaction: Interaction):
        """Handles an event when the AddNewAlbumModal was submitted."""
        logger.info("Received filled in information for new album!")
        await interaction.response.defer(thinking=True)
        # Generate a "receipt embed" with information about the received data
        receipt_embed = Embed(
            title="Kvitto",
            description="Hej, här är ett kvitto på informationen du nyss angav till mig, ifall något skulle bli fel.",
            color=INFO_EMBED_COLOR,
        )
        receipt_embed.add_field(
            name="Albumnamn", value=f"`{self.album_name.value}`", inline=False
        )
        receipt_embed.add_field(
            name="Artister", value=f"`{self.album_artists.value}`", inline=False
        )
        receipt_embed.add_field(
            name="Genrer", value=f"`{self.album_genres.value}`", inline=False
        )
        if self.is_album_of_the_day:
            # Add comments as a text file and add it as a kwarg
            comments_file = BytesIO(self.album_comments.value.encode("UTF-8"))
            extra_kwargs = {"file": File(comments_file, "comments.txt")}
        else:
            extra_kwargs = {}
        self.last_message = await interaction.followup.send(
            embed=receipt_embed, **extra_kwargs
        )
        # First, validate that there is no previous album of the day.'
        previous_entry = await sync_to_async(AlbumOfTheDay.objects.filter)(
            date=get_now().date()
        )
        previous_entry = await sync_to_async(previous_entry.first)()
        if previous_entry is not None:
            logger.critical(
                "An album for today already exists! Asking the user what they want to do..."
            )

            class DeleteAlbumButtons(View):
                """View for when an album of the day already exits,
                and the user can either delete it or cancel the flow to add a new album.
                """

                def __init__(self, parent_view: "AddNewAlbumModal", timeout=180):
                    """Creates a button set for when the album of the day already exists and the user can choose to delete it
                    or abort the action.

                    :param parent_view: A link back to the AddNewAlbumModal instance that the button derives from.
                    """
                    super().__init__(timeout=timeout)
                    self.parent_view = parent_view

                @button(label="Radera", style=ButtonStyle.red)
                async def delete(self, interaction: Interaction, button: Button):
                    await interaction.response.defer()
                    logger.info("Deleting previous album of the day entry...")
                    await sync_to_async(previous_entry.delete)()
                    logger.info("Previous album of the day entry deleted.")
                    await self.parent_view.last_message.reply(
                        embed=Embed(
                            title="Raderat",
                            description="Jag har raderat dagens album of the day. Kör detta kommando igen så kan jag skapa ett nytt.",
                            color=ERROR_EMBED_COLOR,
                        )
                    )

                @button(label="Avbryt", style=ButtonStyle.gray)
                async def abort(self, interaction: Interaction, button: Button):
                    await interaction.response.defer()
                    logger.info("Aborting the action.")
                    await self.parent_view.last_message.reply(
                        embed=generate_error_message(
                            title="Avbrutet",
                            message="Okej, jag kommer inte att göra något.",
                        )
                    )

            self.last_message = await interaction.followup.send(
                embed=generate_error_message(
                    message="Det finns redan en album of the day för idag. Vill du radera den?"
                ),
                view=DeleteAlbumButtons(self),
            )
            return
        logger.info(
            "No previous album of the day detected. Going ahead and splitting stuff..."
        )
        album_artists = self.album_artists.value.split(",")
        album_genres = self.album_genres.value.split(",")
        album_name = self.album_name.value
        album_comments = self.album_comments.value
        # Now, we want to preview what actions we will be doing the user:
        # we want to preview everything that we will be adding, and what
        # previous data we will be using, so the user has a chance to verify
        # that it is correct.
        # Find artists in Django
        for album_artist in album_artists:
            django_artist = await sync_to_async(find_django_artist_from_name)(
                album_artist
            )  # Attempt to find previous entry in database
            (
                self.new_album_artists
                if django_artist is None
                else self.old_album_artists
            )[album_artist] = django_artist
        # Find genres in Django
        for album_genre in album_genres:
            django_genre = await sync_to_async(find_django_genre_from_name)(
                album_genre
            )  # Attempt to find previous entry in database
            (self.new_album_genres if django_genre is None else self.old_album_genres)[
                album_genre
            ] = django_genre
        # Now, create embeds to preview the actions
        # Find album in Django
        if self.is_album_of_the_day:
            self.album_django = await sync_to_async(find_django_album_from_details)(
                artist_names=album_artists, album_name=album_name
            )
            self.album_is_new = (
                self.album_django is None
            )  # Whether a new album is created
        else:  # The action to create a new album will always imply that we're creating new stuff
            self.album_django = None
            self.album_is_new = True
        # Add the two other confirmations
        if self.is_album_of_the_day:
            if self.album_is_new:
                self.things_to_be_confirmed["new_album"] = Embed(
                    title="Förhandsgrandskning: Nytt album",
                    description="Jag hittade inte detta album tidigare i databasen. Stämmer det?",
                    color=SUCCESS_EMBED_COLOR,
                )
            else:
                # Add text to all artists
                # Fetch all old artists from database
                self.things_to_be_confirmed["old_album"] = Embed(
                    title="Förhandsgranskning: Tidigare hittat album:",
                    description=f"""Jag hittade ett tidigare album i databasen. Stämmer det med det album
                                                                 som du vill lägga till?\n
                                                                 **{self.album_django.name}**""",
                    url=f"{os.environ['FRONTEND_BASE_URL']}/albums/{self.album_django.id}",
                    color=WARNING_EMBED_COLOR,
                )
                self.things_to_be_confirmed["old_album"].set_thumbnail(
                    url=self.album_django.cover_url
                )
        # Actions to stuff that will be added
        if len(self.new_album_artists) > 0:
            self.things_to_be_confirmed["new_artists"] = Embed(
                title="Förhandsgranskning: Artister som ska läggas till:",
                description=f"""Jag kommer att lägga till följande artister: 
                                            {list_to_markdown(list(self.new_album_artists.keys()), 
                                                              code_ticks_around_items=True)}""",
                color=WARNING_EMBED_COLOR,
            )
        if len(self.new_album_genres) > 0:
            self.things_to_be_confirmed["new_genres"] = Embed(
                title="Förhandsgranskning: Genrer som ska läggas till:",
                description=f"""Jag kommer att lägga till följande genrer: 
                                        {list_to_markdown(list(self.new_album_genres.keys()), 
                                                          code_ticks_around_items=True)}""",
                color=WARNING_EMBED_COLOR,
            )

        # Actions to old metadata that will be used
        if len(self.old_album_artists) > 0:
            self.things_to_be_confirmed["old_artists"] = Embed(
                title="Förhandsgranskning: Tidigare hittade artister:",
                description=f"""Jag hittade dessa artister i databasen och kommer använda de för albumets metadata. 
                                            Vänligen kolla att de stämmer:
                                            {list_to_markdown([f"`{artist_name}`:`{previous_artist}`" for artist_name, 
                                                                                                          previous_artist in self.old_album_artists.items()])}""",
                color=WARNING_EMBED_COLOR,
            )
        if len(self.old_album_artists) > 0:
            self.things_to_be_confirmed["old_genres"] = Embed(
                title="Förhandsgranskning: Tidigare hittade artister:",
                description=f"""Jag hittade dessa genrer i databasen och kommer använda de för albumets metadata. 
                                                    Vänligen kolla att de stämmer:
                                                    {list_to_markdown([f"`{genre_name}`:`{previous_genre}`" for genre_name,
                                                                                                              previous_genre in self.old_album_genres.items()])}""",
                color=WARNING_EMBED_COLOR,
            )
        logger.info(
            f"Album of the day flow: Starting confirmation flow... (things to be confirmed: {self.things_to_be_confirmed.keys()})"
        )
        await self.confirm_next(interaction)  # Start the confirmation flow


# Define main class
class CreateAlbumOfTheDay(Cog):
    """Bot cog that includes commands for creating a new album of the day."""

    def __init__(self, bot: Bot):
        """Initializes the cog to create album of the days."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @command(description="Adds a new album of the day to the database.")
    async def add_album_of_the_day(self, interaction: Interaction):
        """Adds a new album of the day to the database."""
        self.logger.info(
            "Got a request to add a new album of the day! Sending out information modal..."
        )
        await interaction.response.send_modal(AddNewAlbumModal())


async def setup(bot: Bot):
    """Setup function that is called when the bot loads this extension.

    :param bot: The Discord bot instance."""
    await bot.add_cog(CreateAlbumOfTheDay(bot))
