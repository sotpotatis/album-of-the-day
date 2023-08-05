"""main.py
Runs the bot and loads settings related to it."""
import asyncio
import os, logging, discord, sys
from discord.ext.commands import Bot
from discord.app_commands import CommandTree

# Prerequisites before importing commands: make them know how to talk to Django!
sys.path.append("../..")
os.environ["DJANGO_SETTINGS_MODULE"] = "album_of_the_day.settings"
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


bot = AlbumOfTheDayBot()
logger.info("Running album of the day bot...")
bot.run(BOT_TOKEN)
