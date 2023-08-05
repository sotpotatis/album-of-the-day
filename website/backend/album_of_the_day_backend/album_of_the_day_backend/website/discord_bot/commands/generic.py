"""generic.py
Some generic/various commands: for example a ping command."""
import logging

from discord.ext.commands import Cog
from discord.app_commands import command
from discord import Interaction, Embed
from .utilities import STANDARD_EMBED_COLOR

logger = logging.getLogger(__name__)


class Generic(Cog):
    def __init__(self, bot):
        """Initializes the generic commands cog.."""
        self.bot = bot

    @command()
    async def ping(self, interaction: Interaction):
        """Pings the bot to ensure that it is awake."""
        logger.info("Got a request to send ping information...")
        await interaction.response.send_message(
            embed=Embed(
                title="Pong!",
                description=f"Hej där! Min ping är just nu `{round(self.bot.latency, 2)}ms`.",
                color=STANDARD_EMBED_COLOR,
            )
        )


async def setup(bot):
    await bot.add_cog(Generic(bot))
