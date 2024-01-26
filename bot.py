import logging
import os
import platform
import random
import aiohttp

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

from utils.exp import XpCog
from configs import Configs
from googletrans import Translator
from database import DatabaseManager

intents = discord.Intents.all()


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        current_format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        current_format = current_format.replace("(black)", self.black + self.bold)
        current_format = current_format.replace("(reset)", self.reset)
        current_format = current_format.replace("(levelcolor)", log_color)
        current_format = current_format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(current_format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S",
                                           style="{")
file_handler.setFormatter(file_handler_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

configs = Configs()


async def init_db() -> None:
    async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
    ) as db:
        with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
        ) as file:
            await db.executescript(file.read())
        await db.commit()


mencao_cooldown = commands.CooldownMapping.from_cooldown(1, 120, commands.BucketType.user)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(configs.prefix),
            intents=intents,
            help_command=None,
        )

        self.logger = logger
        self.database = None

    async def load_cogs(self) -> None:

        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"⚙️ > Cog '{extension}' Loaded.")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )

    @tasks.loop(hours=1)
    async def send_daily_quote(self):
        channel_id = configs.codehelp.geral

        async with aiohttp.ClientSession() as session:
            channel = bot.get_channel(channel_id)
            if not channel:
                return

            history = [message async for message in channel.history(limit=1)]

            if history and history[0].author == bot.user:
                return

            async with session.get('https://api.quotable.io/random') as response:
                if response.status == 200:
                    quote_data = await response.json()

                    tradutor = Translator()
                    conteudo_traduzido = tradutor.translate(quote_data['content'], dest='pt').text
                    autor_traduzido = tradutor.translate(quote_data['author'], dest='pt').text

                    message = f"{conteudo_traduzido}\n_{autor_traduzido}_"

                    if channel:
                        await channel.send(message)
                    else:
                        logger.warning(f'cant find {channel_id}')

    @tasks.loop(minutes=3.0)
    async def status_task(self) -> None:

        statuses = [
            "com fubá 🌽",
        ]

        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:

        await self.wait_until_ready()

    async def setup_hook(self) -> None:

        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await init_db()
        await self.load_cogs()
        self.status_task.start()
        self.send_daily_quote.start()

        self.database = DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )

    async def on_message(self, message: discord.Message) -> None:

        if message.author == self.user or message.author.bot:
            return

        if message.author.id == configs.users.tekbox:
            if random.randint(1, 10) > 9:
                await message.add_reaction('<:fuba:1129443906753396847>')

        if bot.user.mentioned_in(message):
            retry_after = mencao_cooldown.get_bucket(message).update_rate_limit()
            if retry_after:
                return
            canal = message.channel
            responses = ['Que passa?', 'tranquilo?', 'aqui que me chamaram?', 'tava dormindo pow >:(']
            await canal.send(f"Oii, {message.author.mention} {responses[random.randint(0,len(responses)-1)]}")
        await XpCog(self).compute_xp(message)
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id}) "
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="Some daqui!", color=0xE02B2B
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="Você não tem permissão pra isso, suma.`",
                color=0xE02B2B)

            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="Não posso fazer isso`",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error


load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))
