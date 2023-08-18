"""main.py
Runs the bot and loads settings related to it."""
import asyncio
import os, logging, discord, sys
from contextvars import Context
from discord.ext.commands import Bot, CommandError
from discord.app_commands import CommandNotFound

# Prerequisites before importing commands: make them know how to talk to Django!
sys.path.append("../..")
os.environ["DJANGO_SETTINGS_MODULE"] = "album_of_the_day.settings"
from commands.utilities import generate_error_message, refresh_database_connections

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.debug("Retrieving bot settings...")
BOT_TOKEN = os.environ["ALBUM_OF_THE_DAY_BOT_TOKEN"]
BOT_COMMAND_PREFIX = os.environ.get(
    "ALBUM_OF_THE_DAY_BOT_COMMAND_PREFIX", "al "
)  # Prefix to call a command
# (but slash commands are used as the default!)
logger.debug("Bot setting retrieved.")
# Set intents
intents = discord.Intents.default()
intents.message_content = True


class AlbumOfTheDayBot(Bot):
    def __init__(self):
        super().__init__(command_prefix=BOT_COMMAND_PREFIX, intents=intents)
        self.initial_extensions = [
            "commands.create_album_of_the_day",
            "commands.generic",
            "commands.create_list",
        ]
        self.logger = logging.getLogger(__name__)  # Create a logger

    async def before_invoke(self, coro):
        """Runs before commands are invoked. Refreshes the database connection."""
        self.logger.info("Pre-command: refreshing database connections...")
        refresh_database_connections()
        self.logger.info("Pre-command: Database connections refreshed.")

    async def setup_hook(self) -> None:
        """Sets up extensions."""
        for extension in self.initial_extensions:
            logger.info(f"Loading cog: {extension}...")
            await self.load_extension(extension)
            logger.info(f"Cog {extension} loaded.")

    async def close(self):
        """Callback that runs when the bot has been closed."""
        await super().close()

    async def on_ready(self):
        logger.info("Bot is ready. Syncing slash commands...")
        await self.tree.sync()
        logger.info("Synced slash commands with Discord.")
        logger.info("Setting status/presence...")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="kommandon | Album of the day bot",
            )
        )
        logger.info("Presence set.")

    async def on_command_error(self, ctx: Context, exception: CommandError, /) -> None:
        """Error handler that runs if the bot encounters an error."""
        # Prevent local handlers
        if hasattr(ctx.command, "on_error"):
            return
        # Get root exception if available
        exception = getattr(exception, "original", exception)
        # If the error is relevant
        if not isinstance(exception, CommandNotFound):
            logger.critical(
                f"The bot encountered an unhandled error: {exception}. Sending error message..."
            )
            error_embed = generate_error_message(
                title="Fel: Ohanterat fel",
                message="Ett ohanterat fel inträffade :( Se nedan för mer info.",
            )
            error_embed.add_field(
                name="Felinformation", value=f"```\n{repr(exception)}```"
            )
            await ctx.send(embed=error_embed)
            logger.info("Error message sent.")


bot = AlbumOfTheDayBot()
logger.info("Running album of the day bot...")
bot.run(BOT_TOKEN)
