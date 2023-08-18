"""utilities.py
Various constants and utilities."""
import datetime
import logging
from difflib import SequenceMatcher

import django.db
import pytz, os
from discord import Color, Embed
from typing import Optional, List, Type, Callable
from django.db.models import Model

# Constants
from discord.utils import get

STANDARD_EMBED_COLOR = Color.lighter_grey()
INFO_EMBED_COLOR = Color.blue()
SUCCESS_EMBED_COLOR = Color.green()
WARNING_EMBED_COLOR = Color.yellow()
ERROR_EMBED_COLOR = Color.red()
LOADING_SPINNER_URL = (
    "https://i.ibb.co/LtQDH8J/loading-spinner.gif"  # URL to a loading spinner URL
)

# Create a logger that may be used by functions
logger = logging.getLogger(__name__)


# Helper functions
def generate_error_message(message, title: Optional[str] = None) -> Embed:
    """Generates an error embed based on details.

    :param message: The error message.

    :param title: A title to use for the embed. Default is "Ett fel inträffade"."""
    if title is None:
        title = "Ett fel inträffade"
    embed = Embed(title=title, description=message, color=ERROR_EMBED_COLOR)
    return embed


def get_now() -> datetime.datetime:
    """Gets the current datetime in the Swedish timezone."""
    return datetime.datetime.now(tz=pytz.timezone("Europe/Stockholm"))


def list_to_markdown(
    input_list: List,
    tab_level: Optional[int] = None,
    code_ticks_around_items: Optional[bool] = None,
) -> str:
    """Formats a list as markdown to send in Discord. Discord doesn't have support for lists,
    but this function attempts to make them a little prettier.

    :param input_list The list of content to include.

    :param tab_level: Optional indentation level of list items. Defaults to one tab.

    :param code_ticks_around_items: If True, all contents will have code ticks (`) around it.
    Defaults to False."""
    # Fill out defaults
    if tab_level is None:
        tab_level = 1
    if code_ticks_around_items is None:
        code_ticks_around_items = False
    output = ""
    # Render text for all list items
    for list_item in input_list:
        output += "\t" * tab_level + "- "
        if code_ticks_around_items:
            output += "`"
        output += str(list_item)
        if code_ticks_around_items:
            output += "`"
        output += "\n"
    return output


def generate_loading_message(message: str, title: Optional[str] = None):
    """Generates a message with a loading spinner to indicate that something is loading.

    :param message The message to display to the user.

    :param title: An optional title. Default is "Laddar..."."""
    if title is None:
        title = "Laddar..."
    loading_embed = Embed(title=title, description=message, color=WARNING_EMBED_COLOR)
    loading_embed.set_thumbnail(url=LOADING_SPINNER_URL)
    return loading_embed


def get_text_similarity(text_1: str, text_2: str) -> float:
    """Gets the similarity between two texts.

    :param text_1: The first text to include in the comparison.

    :param text_2: The second text to include in the comparison."""
    return SequenceMatcher(None, text_1, text_2).ratio()


def get_all(
    thing_to_retrieve: Type[Model],
    is_field: Optional[bool] = None,
    select_function: Optional[Callable] = None,
) -> List[Model]:
    """Somewhat hacky way to get away with loading all Django instances of a certain model
    in an async context. Simply use sync_to_async(get_all) and it'll work. At least here.

    :param django_model: The model or field to get all objects from.

    :param is_field: True if you're fetching a field, False if you are fetching a model.
    (True will not access .objects.all(), but .all() of the thing_to_retrieve argument).

    :param select_function: To customize completely what function to call ".all()" on, pass a callable to this
    parameter. Note that this will override is_field."""
    if is_field is None:  # Fill out defaults
        is_field = False
    model_instances = []
    # Get all objects, append them to a list, and return
    # First determine what to access. See the comment for the is_field argument for more information.
    if select_function is not None:
        thing_accessor = select_function()
    elif not is_field:
        thing_accessor = thing_to_retrieve.objects
    else:
        thing_accessor = thing_to_retrieve
    for model_instance in thing_accessor.all():
        model_instances.append(model_instance)
    return model_instances


def refresh_database_connections():
    """Refreshes Django database connections. This is used to optimize the
    connections used by the bot since they are long-running.
    """
    # Close old connections
    logger.info("Refreshing database connections...")
    closed_connections = 0  # Count number fo closed connections
    for connection in django.db.connections.all():
        connection.close_if_unusable_or_obsolete()
        if (
            connection.connection is None
        ):  # This indicates that the connection has been closed
            closed_connections += 1
    logger.info(f"Closed {closed_connections} old or unusable database connections.")
    # Start a new connection
    django.db.connection.connect()
    logger.info("Updated database connection.")
