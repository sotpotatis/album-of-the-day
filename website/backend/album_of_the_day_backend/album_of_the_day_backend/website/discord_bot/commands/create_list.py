"""create_list.py
Creates album lists. First stores them in memory with the ability
to publish them to the server later on."""
import os

from asgiref.sync import sync_to_async
from discord.ext.commands import Bot, Cog
from discord import Interaction, Client, Button, ButtonStyle, Embed
from discord.ui import View, button, Modal
from discord.app_commands import command, autocomplete, Choice
from typing import Optional, Callable, Tuple, List, Union, Dict
from website.models import AlbumOfTheDay, Artist, Genre, Album, AlbumList, AlbumListItem
from .utilities import (
    get_text_similarity,
    list_to_markdown,
    WARNING_EMBED_COLOR,
    SUCCESS_EMBED_COLOR,
    generate_error_message,
    get_now,
    get_all,
    generate_loading_message,
)
from .create_album_of_the_day import AddNewAlbumModal
import logging, django


django.setup()  # Register Django so we can access models etc.


class ConfirmationView(View):
    def __init__(self, on_confirm: Callable, on_abort: Callable, timeout=180):
        """Initializes a view that contains buttons for confirming or aborting an action.

        :param on_confirm: Action to run when the confirmation button is clicked.

        :param on_abort: Action to run when the abort button is clicked.

        Note: the functions on_confirm and on_abort receives the interaction variable
        as an argument."""
        super().__init__(timeout=timeout)
        self.on_confirm = on_confirm
        self.on_abort = on_abort
        self.logger = logging.getLogger(__name__)

    @button(label="Godkänn", style=ButtonStyle.green)
    async def on_confirm(self, interaction: Interaction, button: Button):
        self.logger.info("User pressed the confirmation button. Running action...")
        await self.on_confirm(interaction)

    @button(label="Avbryt", style=ButtonStyle.red)
    async def on_abort(self, interaction: Interaction, button: Button):
        self.logger.info("User pressed the abort button. Running action...")
        await self.on_abort(interaction)


class CreateAlbumList(Cog):
    """A cog for creating album lists."""

    def __init__(self, bot: Bot):
        """Initializes the cog to create album lists."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        # Lists are stored in the bot's memory before they are removed.
        # Format: (<list data>,<list items>,<list is new or not>,)
        # For each list item, a tuple containing this is included:
        # (<if item is new: a dict with kwargs to pass to AlbumListItem, otherwise a previous instance of
        # an AlbumListItem>, <if the item is new>,)
        self.LIST_STORAGE: List[
            Tuple[AlbumList, List[Tuple[Union[AlbumListItem, dict], bool]], bool]
        ] = []
        self.last_message = None  # Store the last message
        # Used for list autocomplete
        self.list_cache: List[Tuple[AlbumList, List[AlbumListItem]]] = []
        self.lists_last_downloaded_at = None
        # Used for album autocomplete
        self.albums_list: List[Album] = []
        self.albums_last_downloaded_at = None

    async def validate_album_list(
        self, album_list_index: int, interaction: Interaction
    ) -> bool:
        """Validates that an album list index is valid. I thought
        Discord had an option to limit slash commands to only autocompleted ones, but apparently not.

        :param album_list_index: The index of the album list that the user requests.

        :param interaction: An interaction to send out an error message to directly in case the list index is not valid.

        :returns True if the validation succeeded, False if it failed."""
        if album_list_index < 0 or album_list_index > len(self.LIST_STORAGE) - 1:
            await interaction.followup.send(
                embed=generate_error_message(
                    message="Felaktigt listindex. Listan du valde finns inte. Se till att du inte skrev in ett val manuellt."
                )
            )
            return False
        return True

    async def sync_remote_albums(self) -> None:
        """Syncs albums from the remote server if needed.
        This is so that the bot can autocomplete albums inside of commands."""
        # Determine if we should download albums or not
        if (
            self.albums_last_downloaded_at is None
            or (get_now() - self.albums_last_downloaded_at).total_seconds() > 360
        ):
            self.logger.info("Syncing albums from remote server...")
            # Get all Album objects. Also prefetch the related "artists" field that is being accessed
            # (the "genres" field is not being accessed, so we do not prefetch it)
            self.albums_list = await sync_to_async(get_all)(
                Album,
                select_function=lambda: Album.objects.all().prefetch_related("artists"),
            )
            self.albums_last_downloaded_at = get_now()
            self.logger.info("Albums were synced.")

    async def sync_remote_lists(self) -> None:
        """Syncs lists from the remote server if needed.
        This is so that the bot can autocomplete lists inside of commands."""
        # Determine if we should download lists or not
        if (
            self.lists_last_downloaded_at is None
            or (get_now() - self.lists_last_downloaded_at).total_seconds() > 380
        ):
            self.logger.info("Syncing lists from database...")
            # Get all AlbumList objects. Prefetch the list items.
            all_album_lists = await sync_to_async(get_all)(
                AlbumList,
                select_function=lambda: AlbumList.objects.all().prefetch_related(
                    "items"
                ),
            )
            for album_list in all_album_lists:
                all_list_items = await sync_to_async(get_all)(album_list.items, True)
                self.list_cache.append(
                    (  # Add the data and mark the list as not new
                        album_list,
                        all_list_items,
                    )
                )
            self.lists_last_downloaded_at = (
                get_now()
            )  # Save when lists were last synced
            self.logger.info("Lists were synced from remote and added to cache.")

    async def on_abort(self, interaction: Interaction):
        """Helper/shortcut function that sends a message when an action has been aborted."""
        await interaction.response.defer()
        self.last_message = await self.last_message.reply(
            embed=generate_error_message(
                title="Avbruten",
                message="Åtgärden avbröts. Kör kommandot igen om du vill börja om.",
            )
        )

    def get_album_list_item_values(
        self, album_list_item: Union[AlbumListItem, dict], album_list_item_is_new: bool
    ) -> Dict:
        """Since I set this up a little wonkily, album list items can both be AlbumListItems
        or dicts. This fucntion supports getting values from both of them and it additionally replaces any empty
        text fields with None.

        :param album_list_item: The album list item to get the values from.

        :param album_list_item_is_new: Whether the album list is new or not.

        Note that the two arguments to this function can be retrieved by unpacking the value
        of self.LIST_STORAGE[<relevant list index>]"""
        results = {}  # Return results as a dictionary
        if album_list_item_is_new:
            results["album"] = album_list_item.get("album", None)
            results["comments"] = album_list_item.get("comments", None)
            results["heading"] = album_list_item.get("heading", None)
            results["body"] = album_list_item.get("body", None)
        else:  # If the item is not new, we'd have an AlbumListItem here,
            # and it does not support getitem.
            results["album"] = album_list_item.album
            results["comments"] = album_list_item.comments
            results["heading"] = album_list_item.heading
            results["body"] = album_list_item.body
        # Translate empty fields to None
        final_results = {}
        for key, value in results.items():
            final_results[key] = None if value in [None, ""] else value
        return final_results

    @command(name="create_album_list", description="Creates a new album list.")
    async def create_album_list_command(
        self, interaction: Interaction, list_name: str, list_description: str
    ):
        self.logger.info("Got a request to create a new album list!")
        # Warn if the album list has not already been created
        similar_lists = []
        for previous_album_list_data, _, _ in self.LIST_STORAGE:
            previous_album_list = previous_album_list_data[0]
            if get_text_similarity(list_name, previous_album_list.name) > 0.8:
                similar_lists.append(previous_album_list.name)
        if len(similar_lists) > 0:
            self.logger.info(
                "Similar lists found. Sending confirmation message to ask the user what to do."
            )

            # Create a callback for the ConfirmationView
            def on_confirm(interaction: Interaction):
                self.create_album_list(interaction, list_name, list_description)

            self.last_message = await interaction.followup.send(
                embed=Embed(
                    title="Möjliga liknande listor hittades",
                    description=f"""Jag hittade några listor som möjligtvis är lika denna. Är du säker på att du vill skapa 
                en ny lista och inte redigera de? Liknande listor:
                {list_to_markdown(similar_lists)}""",
                    color=WARNING_EMBED_COLOR,
                ),
                view=ConfirmationView(on_confirm=on_confirm, on_abort=self.on_abort),
            )
        else:
            self.logger.info(
                "No similar album lists found. Proceeding with adding and creating the new one..."
            )
            await self.create_album_list(interaction, list_name, list_description)

    async def create_album_list(
        self, interaction: Interaction, list_name: str, list_description: str
    ):
        """Creates a new album list in memory and then sends a confirmation message.

        ¨:param interaction: An interaction that we can respond to when we are done adding the list.

        :param list_name: The name of the new list.

        :param list_description: The description of the new list."""
        await interaction.response.defer()
        self.LIST_STORAGE.append(
            (AlbumList(name=list_name, description=list_description), [], True)
        )
        self.logger.info(
            "Created a new album list in memory. Sending confirmation message..."
        )
        self.last_message = await interaction.followup.send(
            embed=Embed(
                title="Skapad!",
                description="""Albumlistan har skapats i minnet. Använd kommandon som `/add_album_to_list`,
             `/add_field_to_list` etc. för att redigera den.""",
                color=SUCCESS_EMBED_COLOR,
            )
        )

    @command(
        name="clear_album_lists",
        description="Clear all album lists that are stored in memory.",
    )
    async def clear_album_lists_memory_command(self, interaction: Interaction):
        """Command that clears album lists stored in the memory.

        :param interaction: The interaction that was invoked from using this command."""
        await interaction.response.defer()
        self.logger.info(
            "Got a request to clear album lists. Asking for confirmation..."
        )
        if len(self.LIST_STORAGE) > 0:
            self.last_message = await interaction.followup.send(
                embed=generate_error_message(
                    title="Är du säker?",
                    message=f"""Detta kommer att **RADERA** {len(self.LIST_STORAGE)} sparade albumlistor. 
                (i minnet, inte på servern)""",
                ),
                view=ConfirmationView(
                    on_confirm=self.clear_album_lists_memory, on_abort=self.on_abort
                ),
            )
        else:
            self.logger.info("No confirmation needed, the lists are already empty.")
            self.last_message = await interaction.followup.send(
                embed=generate_error_message(
                    title="Inga listor att radera.",
                    message="Det finns inga listor sparade i minnet.",
                )
            )

    async def clear_album_lists_memory(self, interaction: Interaction):
        """Clears album lists that are stored in memory."""
        self.logger.info("Clearing album lists that are stored in memory...")
        await interaction.response.defer()
        self.LIST_STORAGE = []
        self.logger.info("List storage cleared. Sending confirmation message...")
        self.last_message = await self.last_message.reply(
            embed=Embed(
                title="✅ Rensat!",
                description="Jag har rensat de albumlistorna som var sparade i minnet.",
                color=SUCCESS_EMBED_COLOR,
            )
        )

    @command(description="Downloads a list from the database to edit in the bot.")
    async def download_list_from_database(
        self, interaction: Interaction, list_to_download: int
    ):
        """Downloads a list from the database to the local memory so it can be edited.

        :param interaction: The interaction that invoked this command.

        :param list_to_download: The ID of the list to download from cloud."""
        await interaction.response.defer()
        self.logger.info("Got a request to download a list from the database.")
        self.last_message = (
            album_list_loading_message
        ) = await interaction.followup.send(
            embed=generate_loading_message(
                message="Laddar ner lista från databasen. Snart klar!"
            )
        )
        self.logger.info("Downloading list...")
        album_list = await sync_to_async(AlbumList.objects.filter)(id=list_to_download)
        album_list = await sync_to_async(album_list.first)()
        if album_list is None:  # If the list is not found
            self.logger.warning(f"Could not find album list {list_to_download}!")
            self.last_message = await self.last_message.reply(
                embed=generate_error_message(
                    message="Albumlistan hittades inte. Testa med ett annat val."
                )
            )
            return
        self.logger.info("Album list fetched. Fetching items...")
        await self.last_message.edit(
            embed=generate_loading_message(
                message="Listan har laddats ner. Laddar ner innehåll..."
            )
        )
        # To get all the albums from an async context, we prefetch any related fields from Django.
        album_list_items = await sync_to_async(get_all)(
            album_list.items,
            select_function=lambda: AlbumList.objects.prefetch_related("items")
            .filter(id=list_to_download)
            .first()
            .items.all()
            .prefetch_related("album"),
        )
        self.logger.info("Items fetched. Saving...")
        self.LIST_STORAGE.append(
            (
                album_list,
                [
                    (album_list_item, False)  # Mark all album list items as old
                    for album_list_item in album_list_items
                ],
                False,
            )
        )
        self.logger.info("The list has been fetched and saved in storage.")
        self.last_message = await self.last_message.reply(
            embed=Embed(
                title="✅ Nedladdad!",
                description="Listan har laddats ner och du kan nu göra ändringar på den.",
                color=SUCCESS_EMBED_COLOR,
            )
        )
        await album_list_loading_message.delete()

    @download_list_from_database.autocomplete("list_to_download")
    async def autocomplete_lists_to_download(
        self, interaction: Interaction, current_value: str
    ) -> List[Choice[str]]:
        """Autocompletion for album lists for the download list from database command."""
        await self.sync_remote_lists()
        # Autocomplete
        possible_options = []
        for album_list, _ in self.list_cache:
            if current_value.lower() in album_list.name.lower():
                possible_options.append(
                    Choice(name=album_list.name, value=album_list.id)
                )
        # Ensure possible_options doesn't exceed 25 options
        if len(possible_options) > 25:
            possible_options = possible_options[:24]
        return possible_options

    @command(description="Lägg till ett album till en lista.")
    async def add_album_to_list(
        self,
        interaction: Interaction,
        album_list: int,
        album_id: str,
        comments: Optional[str] = None,
    ):
        """Adds an album to a list that is saved in the bot's memory.

        :param interaction: The interaction that was invoked from the use of this slash command.

        :param album_list: The album list to add the album to.

        :param album_id: The ID of the album to add.

        :param comments: Any comments to add to the album."""
        self.logger.info("Got a request to add an album to a list.")
        # Validate that the album list actually exists
        album_list_is_valid = await self.validate_album_list(album_list, interaction)
        if not album_list_is_valid:  # Abort if the album list was not found
            self.logger.warning("Album list was not found - aborting.")
            return
        confirmation_embed = Embed(  # Create an embed for when we are done
            title="✅ Albumet lades till i listan.",
            description="Jag har lagt till albumet i listan.",
            color=SUCCESS_EMBED_COLOR,
        )
        if (
            album_id == "new"
        ):  # If the album ID is this, the invoker wants to create a new album.
            self.logger.info("The user wants to create a new album.")

            # Now, we show a modal to the user to create a new album.
            async def on_album_addition(new_album: Album):
                """Callback that runs when an album has been created and added."""
                self.logger.info("The album has been added.")
                # Create data for the album
                album_data = {"album": new_album}
                if comments is not None:
                    album_data["comments"] = comments
                self.LIST_STORAGE[album_list][1].append((album_data, True))
                await self.last_message.reply(embed=confirmation_embed)

            new_album_modal = AddNewAlbumModal(
                is_album_of_the_day=False, on_done=on_album_addition
            )
            await interaction.response.send_modal(new_album_modal)
        else:
            await interaction.response.defer()
            # album_id will be a valid integer in this case - but the user can still add illegal data so cover it
            try:
                album_id = int(album_id)
            except:
                self.logger.warning(
                    "Album_id is not a valid integer. Sending error message.."
                )
                await interaction.response.send(
                    embed=generate_error_message(
                        message="Efterfrågat album-ID är inte en giltig siffra. Se till att du inte har angivit ett värde manuellt."
                    )
                )
                return
            self.logger.info("Using a previous album. Adding it to the list...")
            if (
                album_id < 0 or album_id > len(self.albums_list) - 1
            ):  # Validate album list
                self.logger.warning(
                    "Entered album ID is invalid. Sending error message..."
                )
                await interaction.followup.send(
                    embed=generate_error_message(
                        message="Felaktigt album-ID. Se till att du inte har angivit ett värde manuellt."
                    )
                )
                return
            else:
                album_data = {"album": self.albums_list[album_id]}
                # Add comments if existent
                if comments is not None:
                    album_data["comments"] = comments
                self.LIST_STORAGE[album_list][1].append((album_data, True))
                self.logger.info("Album added to list. Sending confirmation...")
                self.last_message = await interaction.followup.send(
                    embed=confirmation_embed
                )

    @add_album_to_list.autocomplete("album_id")
    async def autocomplete_album_id(
        self, interaction: Interaction, current_value: str
    ) -> List[Choice[str]]:
        """Autocompletes the album_id field, returning remote albums or the option to sync local albums."""
        await self.sync_remote_albums()
        # Start the autocompletion
        possible_options = []
        for i in range(len(self.albums_list)):
            album = self.albums_list[i]
            album_artists = await sync_to_async(get_all)(album.artists, True)
            # Generate a string that contains information about the album
            album_information = ""
            for album_artist in album_artists:
                album_information += f"{album_artist.name} & "
            # Add album name
            album_information = album_information.strip("& ")
            album_information += f" - {album.name}"
            # Generate a choice for the album
            album_choice = Choice(name=album_information, value=str(i))
            # First look for wht the user entered in the album name
            if current_value.lower() in album.name.lower():
                possible_options.append(album_choice)
            else:  # Look in the artists instead
                for album_artist in album_artists:
                    if current_value.lower() in album_artist.name.lower():
                        possible_options.append(album_choice)
        # Discord only allows 25 fields inside an autocomplete
        # ...and Discord.py does not raise an error about it...
        # (we add one field below so we limit to 24 entries)
        if len(possible_options) > 24:
            possible_options = possible_options[:23]
        #  We give the option to create a new album as well.
        possible_options.append(Choice(name="Lägg till ett nytt album", value="new"))
        return possible_options

    @command(description="Lägg till ett fält till en lista.")
    async def add_field_to_list(
        self,
        interaction: Interaction,
        album_list: int,
        heading: Optional[str] = None,
        text: Optional[str] = None,
    ):
        """Adds a field to an album list.

        :param interaction: The interaction that was invoked from the usage of this slash command.

        :param album_list: The album list to use.

        :param heading: The heading of the field.

        :param text: The text to include in the field."""
        self.logger.info("Got a request to add a field to list.")
        await interaction.response.defer()
        # Both are optional, but only separately - at least one must be specified.
        if heading is None and text is None:
            self.logger.info("Heading and text is unspecified. Sending message...")
            await interaction.followup.send(
                embed=generate_error_message(
                    message="Du har varken angivit en rubrik eller en text. Minst en av dessa måste vara specificerad."
                )
            )
            return
        self.logger.info("Adding field to list...")
        # Represent the field data as a dictionary.
        field_data = {}
        if heading is not None:
            field_data["heading"] = heading
        if text is not None:
            field_data["body"] = text
        self.LIST_STORAGE[album_list][1].append((field_data, True))
        self.logger.info(
            "The field was added to the list. Sending confirmation message..."
        )
        await interaction.followup.send(
            embed=Embed(
                title="✅ Tillagd i listan",
                description="Jag lade till fältet i listan.",
                color=SUCCESS_EMBED_COLOR,
            )
        )
        self.logger.info("Confirmation message sent.")

    async def sync_list_with_cloud(self, album_list: int):
        """Syncs a specific album list with the cloud database.

        :param album_list: The index of the list to sync."""
        self.logger.info("Starting syncing a list with the cloud...")
        album_list, album_list_items, album_list_is_new = self.LIST_STORAGE[album_list]
        # Begin with creating the album list if it is new
        if album_list_is_new:
            self.logger.info("Creating album list...")
            await sync_to_async(album_list.save)()
            self.logger.info("The album list has been created.")
        else:
            self.logger.info(
                "Interfacing with a previously created album list. It does not have to be created."
            )
        i = 1
        for item_data, item_is_new in album_list_items:  # Iterate over every item
            # Create a new field based on the item_data
            # To delete an item from an existent album list, you can replace the data entry with the following:
            # {"previous": <previous item index>}
            if item_is_new or isinstance(item_data, dict):
                previous_item = item_data.get("previous", None)
                album_list_item_kwargs = item_data
                album_list_item_kwargs["index_in_list"] = i
                # Since the .album field is a ManyToMany-relationship, we have to add it later.
                # So this a somewhat hacky way to get around it.
                """album_list_item_album = None
                if "album" in album_list_item_kwargs:
                    album_list_item_album = album_list_item_kwargs["album"]
                    del album_list_item_kwargs["album"]"""
                if item_is_new:
                    if previous_item is None:
                        new_item = AlbumListItem(**album_list_item_kwargs)
                        self.logger.info(f"Adding album list item {item_data}...")
                        await sync_to_async(new_item.save)()
                        self.logger.info(
                            "The new album list item was added. Adding it to the album list..."
                        )
                        await sync_to_async(album_list.items.add)(new_item)
                        self.logger.info(
                            "The album list item has been added to the album list."
                        )
                        """if album_list_item_album is not None:
                            self.logger.info("Adding album to album list item...")
                            await sync_to_async(new_item.album.add)(album_list_item_album)
                            self.logger.info("Album was added to album list.")"""
                    else:
                        self.logger.info("Removing album list item...")
                        await sync_to_async(item_data["previous"].delete)()
                        self.logger.info("Previous album list item deleted.")
                else:
                    self.logger.info(
                        f"The album list item {item_data} is not new. Not adding it."
                    )
                    # If the album list item is not new, chances are that its index still has to be synced
                    if (
                        album_list_item_kwargs["index_in_list"]
                        != item_data.index_in_list
                    ):
                        self.logger.info("Syncing list indexes with remote item...")
                        item_data.index_in_list = album_list_item_kwargs[
                            "index_in_list"
                        ]
                        await sync_to_async(item_data.save)()
                        self.logger.info("List indexes synced.")
                if previous_item is None:
                    i += 1

    @command(
        name="sync_list_with_cloud",
        description="Synkroniserar en viss albumlista med databasen. Sparar/laddar upp alla ändringar.",
    )
    async def sync_list_with_cloud_command(
        self, interaction: Interaction, album_list: int
    ):
        """Syncs a specific list with the cloud.

        :param interaction: The interaction that was invoked by the use of this slash command.

        :param album_list: The index of the list to sync."""
        await interaction.response.defer()
        self.logger.info("Got a request to sync an album list to the database...")
        # Validate that the album list actually exists
        album_list_is_valid = await self.validate_album_list(album_list, interaction)
        if not album_list_is_valid:  # Abort if the album list was not found
            self.logger.warning("Album list was not found - aborting.")
            return
        await self.sync_list_with_cloud(album_list)
        self.logger.info(
            "The album list has been synced. Sending confirmation message..."
        )
        await interaction.followup.send(
            embed=Embed(
                title="✅ Lista synkroniserad med molnet!",
                description="""Listan har synkroniserats med molnet (databasen) och borde
            nu gå att se på hemsidan.""",
                color=SUCCESS_EMBED_COLOR,
                url=f"{os.environ['FRONTEND_BASE_URL']}/lists/{album_list}",
            )
        )
        # Remove the list from the list storage
        del self.LIST_STORAGE[album_list]

    @command(
        description="""Synkroniserar alla albumlistor med databasen. Sparar/laddar upp alla ändringar."""
    )
    async def sync_all_lists_with_cloud(self, interaction: Interaction):
        """Syncs all lists that are stored in the self.LIST_STORAGE to the remote database.

        :param interaction: The interaction that was invoked by the use of a slash command.
        """
        self.logger.info("Got a request to sync all the lists with the cloud.")
        await interaction.response.defer()
        # Create each list
        last_message = None
        for album_list_id in range(len(self.LIST_STORAGE)):
            self.logger.info(f"Syncing list {album_list_id} to cloud...")
            album_list, album_list_items, album_list_is_new = self.LIST_STORAGE[
                album_list_id
            ]
            # Generate loading message
            creation_message = f"""{'Skapar' if album_list_is_new else 'Uppdaterar'}
                                lista {album_list.name} ({album_list_id+1}/{len(self.LIST_STORAGE)})"""
            last_message = loading_message = await (
                interaction.followup.send
                if last_message is None
                else last_message.reply
            )(embed=generate_loading_message(message=creation_message))
            await self.sync_list_with_cloud(album_list_id)
            await last_message.reply(
                embed=Embed(
                    title="✅ Lista synkad",
                    description=f"Listan {album_list.name} har nu synkats med databasen i molnet. ☁️",
                    color=SUCCESS_EMBED_COLOR,
                )
            )
            await loading_message.delete()  # Delete the loading message
            self.logger.info(f"Synced the list {album_list_id} to cloud.")
        # Empty the list storage
        self.LIST_STORAGE = []

    @command(description="Tar bort ett album eller en textdel från en albumlista.")
    async def remove_item_from_list(
        self, interaction: Interaction, album_list: int, item_to_remove: int
    ):
        """Removes an item from an album list.

        :param interaction: The interaction that was invoked by the use of this slash command.

        :param album_list: The album list to remove items from.

        :param item_to_remove: The index of the item to remove."""
        await interaction.response.defer()
        self.logger.info(f"Removing item from album list {album_list}...")
        # Validate that the album list actually exists
        album_list_is_valid = await self.validate_album_list(album_list, interaction)
        if not album_list_is_valid:  # Abort if the album list was not found
            self.logger.warning("Album list was not found - aborting.")
            return
        # Get the item in the album list
        (
            requested_album_list,
            requested_album_list_items,
            requested_album_list_is_new,
        ) = self.LIST_STORAGE[album_list]
        (
            requested_album_list_item,
            requested_album_list_item_is_new,
        ) = requested_album_list_items[item_to_remove]
        # If the album list is not new, we replace the data of that index instead of remove it
        if (
            requested_album_list_is_new and requested_album_list_item_is_new
        ):  # Check if the album list is not new
            self.logger.info("Item is new, removing directly..")
            del self.LIST_STORAGE[album_list][1][item_to_remove]
        else:  # Replace the item data with {"previous": <old item>} to indicate removal
            self.logger.info("Item is not new, scheduling for removal...")
            self.LIST_STORAGE[album_list][1][item_to_remove] = (
                {"previous": requested_album_list_item},
                True,
            )
        await interaction.followup.send(
            embed=Embed(
                title="✅ Borttagen",
                description="""Den efterfrågade saken att ta bort har tagits bort i minnet.
                         Om du arbetar med en lista som tidigare existerar på servern kommer den att tas bort vid nästa synkning.""",
                color=SUCCESS_EMBED_COLOR,
            )
        )

    @remove_item_from_list.autocomplete("item_to_remove")
    async def autocomplete_item_to_remove(
        self, interaction: Interaction, current_value: str
    ) -> List[Choice[int]]:
        """Autocompletes the item_to_remove field inside a list. Uses the previously set list to get and suggest items."""
        # Get the filled out list items.
        _, list_items, _ = self.LIST_STORAGE[interaction.namespace.album_list]
        possible_options = []
        i = 0
        for list_item, list_item_is_new in list_items:
            # Detect list item type to get which fields
            # to search in
            list_item_values = self.get_album_list_item_values(
                list_item, list_item_is_new
            )
            if list_item_values["album"] is not None:  # If the field is an album entry
                fields_to_check = [list_item_values["album"].name]
                if list_item_values["comments"] is not None:
                    fields_to_check.append(list_item_values["comments"])
            else:  # If the field is a text entry
                fields_to_check = []
                if list_item_values["heading"] is not None:
                    fields_to_check.append(list_item_values["heading"])
                elif list_item_values["body"] is not None:
                    fields_to_check.append(list_item_values["body"])
            # Check all fields for the current value
            for field_to_check in fields_to_check:
                if current_value.lower() in field_to_check.lower():
                    possible_options.append(
                        Choice(name=f"{i+1}. {fields_to_check[0]}", value=i)
                    )
            i += 1
        # Limit possible options to 25
        if len(possible_options) > 25:
            possible_options = possible_options[:24]
        return possible_options

    @command(description="Förhandsgranskar en albumlista och dess innehåll.")
    async def show_list(self, interaction: Interaction, album_list: int):
        """Shows/previews an album list and its items."""
        await interaction.response.defer()
        # Validate that the album list actually exists
        album_list_is_valid = await self.validate_album_list(album_list, interaction)
        if not album_list_is_valid:  # Abort if the album list was not found
            self.logger.warning("Album list was not found - aborting.")
            return
        self.logger.info("Got a request to show an album list. Creating embed...")
        # Split embeds since Discord has a character limit.
        album_list_embeds = []
        current_character_length = 0
        current_embed_entries = []  # Current entries in the embed
        album_list, album_list_items, album_list_is_new = self.LIST_STORAGE[album_list]
        # Create a base embed with information about the bot
        base_embed_title = (
            f"{album_list.name} ({'ny' if album_list_is_new else 'gammal'})"
        )
        base_embed_description = "Se nedan för listans innehåll."
        base_embed = Embed(
            title=base_embed_title,
            description=base_embed_description,
            color=WARNING_EMBED_COLOR,
        )
        # Total length of base embed text
        base_character_length = len(base_embed_title) + len(base_embed_description)
        current_embed = None
        for album_list_item, album_list_item_is_new in album_list_items:
            if current_embed is None:  # Reset embed if needed
                current_embed = base_embed.copy()
            album_list_item_text = None
            album_list_item_title = None
            # Create a human-readable text for the album entry.
            # If it is an album, we create one kind of text. And otherwise, we create another!
            album_list_item_values = self.get_album_list_item_values(
                album_list_item, album_list_item_is_new
            )
            if (
                album_list_item_values["album"] is not None
            ):  # Create text for a list entry album field
                album_list_item_title = f"**{album_list_item_values['album'].name}**\n"
                if album_list_item_values["comments"] is not None:
                    album_list_item_text = (
                        f"```\n{album_list_item_values['comments']}```"
                    )
                else:
                    album_list_item_text = ""
            else:  # Create text for a list entry text field
                album_list_item_text = ""
                if album_list_item_values["heading"] is not None:
                    album_list_item_title = f"**{album_list_item_values['heading']}**\n"
                else:  # If there is no heading
                    album_list_item_title = "[ingen titel]"
                if album_list_item_values["body"] is not None:
                    album_list_item_body_text = album_list_item_values["body"]
                    # Show maximum 500 chars of body text
                    if len(album_list_item_body_text) > 495:
                        album_list_item_body_text = (
                            f"{album_list_item_body_text[:495]}[...]"
                        )
                    album_list_item_text = f"```\n{album_list_item_body_text}```"
                else:  # If there is no body text
                    album_list_item_text = "[ingen brödtext]"
            # Check if embed should be reset
            album_list_item_text_length = len(album_list_item_text) + len(
                album_list_item_title
            )
            # (hard character limit is a little bigger, but we are chill)
            if (
                current_character_length + album_list_item_text_length > 5900
                or len(current_embed.fields) > 23
            ):
                # Rotate embeds
                self.logger.info("Rotating embeds...")
                current_embed_entries.append(current_embed)
                current_embed = None
                current_character_length = base_character_length
            else:
                self.logger.debug(
                    f"Embeds should not be rotated yet (current character length for embed is {current_character_length})."
                )
            current_character_length += album_list_item_text_length
            current_embed.add_field(
                name=album_list_item_title, value=album_list_item_text, inline=False
            )
        # Add the current embed to the list of embeds (note that current_embed = None if the embed was just reset)
        if current_embed is not None:
            current_embed_entries.append(current_embed)
        # Send all embeds
        self.logger.info(
            f"Sending all embeds with information about the current list ({album_list.name})..."
        )
        last_message = None
        number_of_embeds = len(current_embed_entries)
        for i in range(number_of_embeds):
            embed_to_send = current_embed_entries[i]
            self.logger.info(f"Sending embed {i+1}/{number_of_embeds}...")
            # Send a new message for the first time, otherwise reply to old messages
            last_message = await (
                interaction.followup.send
                if last_message is None
                else last_message.reply
            )(embed=embed_to_send)
            self.logger.info(f"Embed {i+1}/{number_of_embeds} sent.")
        self.logger.info("All information embeds sent.")

    # Autocompletes the album list field. Used for multiple commands
    @add_album_to_list.autocomplete("album_list")
    @add_field_to_list.autocomplete("album_list")
    @remove_item_from_list.autocomplete("album_list")
    @show_list.autocomplete("album_list")
    @sync_list_with_cloud_command.autocomplete("album_list")
    async def autocomplete_album_list(
        self, interaction: Interaction, current_value: str
    ) -> List[Choice[int]]:
        """Autocompletes fields where you choose from an album list that is saved in memory."""
        possible_options = []
        for i in range(len(self.LIST_STORAGE)):
            album_list, _, album_list_is_new = self.LIST_STORAGE[i]
            if current_value.lower() in album_list.name.lower():
                possible_options.append(
                    Choice(
                        name=f"Lista {album_list.name} ({'ny' if album_list_is_new else 'gammal'})",
                        value=i,
                    )
                )
        return possible_options

    @command(description="Shows the contents of the list storage in memory.")
    async def dump_list_storage(self, interaction):
        """Command that can be used to "dump" the pure contents of the list storage.
        Only intended for debugging - does not check character limits etc."""
        await interaction.response.defer()
        self.logger.info("Got a request to dump list storage. Doing so...")
        await interaction.followup.send(
            embed=Embed(
                title="📄 Innehållsdump",
                description=f"Här är innehållet i listlagringen:\n```python\n{self.LIST_STORAGE}```",
            )
        )
        self.logger.info("List storage dump sent.")


async def setup(bot: Bot):
    """Setup function that is called when the bot loads this extension.

    :param bot: The Discord bot instance."""
    cog = CreateAlbumList(bot=bot)
    # Prepare autocomplete right away!
    await cog.sync_remote_albums()
    await cog.sync_remote_lists()
    await bot.add_cog(cog)
