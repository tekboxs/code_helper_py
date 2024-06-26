import datetime
import json
import logging
import os
import platform
import random
import sys
import aiohttp
import aiohttp

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
from cogs.roles import MealDropdownView, ProgrammingRoles
from configs import Configs
from googletrans import Translator
from cogs.roles import MealDropdownView, ProgrammingRoles
from configs import Configs
from googletrans import Translator
import os
import subprocess
import spacy
from spacy.util import is_package
from firebase import FirestoreManager

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore







intents = discord.Intents.all()

# modelo_linguagem = 'pt_core_news_lg'

# # Verifica se o modelo já está instalado
# if is_package(modelo_linguagem):
#     print(f'O modelo {modelo_linguagem} já está instalado.')
# else:
#     # Executa o comando de download usando subprocess
#     comando_download = f'python -m spacy download {modelo_linguagem}'
#     resultado = subprocess.run(comando_download, shell=True, check=True, capture_output=True, text=True)

#     # Verifica se o download foi bem-sucedido
#     if resultado.returncode == 0:
#         print(f'O modelo {modelo_linguagem} foi baixado com sucesso.')
#     else:
#         print(f'Ocorreu um erro durante o download: {resultado.stderr}')

# # Carrega o modelo (pode ser feito independentemente do download)
# nlp = spacy.load(modelo_linguagem)

messages_data = {}

# Dicionário para armazenar respostas aprendidas
learned_responses = {'positive': {}, 'negative': {}}


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

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S",
                                           style="{")
file_handler.setFormatter(file_handler_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

configs = Configs()


 
configs = Configs()

 

mencion_cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)
error_cooldown = commands.CooldownMapping.from_cooldown(1, 120, commands.BucketType.user)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(configs.prefix),
            intents=intents,
            help_command=None,
        )

        self.logger = logger

        self.database: FirestoreManager | None = None


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
            "🌽🌽",
            "🌽 de fubá",
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
        
        await self.load_cogs()
        self.status_task.start()
        self.send_daily_quote.start()


        cred = credentials.Certificate(f"{os.path.realpath(os.path.dirname(__file__))}/firebase/key.json")
        app = firebase_admin.initialize_app(cred)
        self.database = FirestoreManager(app)

    async def on_message(self, message: discord.Message) -> None:

        if message.author == self.user or message.author.bot:
            return

        if message.author.id == configs.users.tekbox:
            if random.randint(1, 10) > 9:
                await message.add_reaction('<:fuba:1129443906753396847>')

        if bot.user.mentioned_in(message):
            retry_after = mencion_cooldown.get_bucket(message).update_rate_limit()
            if retry_after:
                return


            responses = ['Chora', 'Eu sou o cara :P', 'Invejosa', 'Sai fora kk',
             'Mas e o bolo de fubá?', 'Eu vou é dormir', 'Me dá bolo de fubá',
             'Vou nessa, como um ninja nas sombras', 'Nem a Netflix tem esse enredo',
             'Parece uma playlist de sentimentos em 7 músicas', 'Quem disse que eu não sou um unicórnio disfarçado?',
             'Deixa que eu resolvo isso com a força do abraço', 'Um dia eu ainda aprendo a fazer origami de pão',
             'Vou responder isso com uma dança interpretativa', 'Você já viu um pato malabarista? Eu também não, mas seria legal',
             'Enquanto isso, na dimensão paralela do bolo cósmico...', 'Isso me lembra da vez que um pombo me deu conselhos de vida',
             'Se eu fosse uma cor, seria o azul do céu num dia sem nuvens', 'Um dia vou descobrir o segredo da meia que sempre some',
             'Meu superpoder é fazer as plantas crescerem mais rápido só com o olhar', 'Sério, preciso desvendar o mistério do bolo de fubá']
            await message.reply(responses[random.randint(0, len(responses) - 1)])


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
    
    error_users_history = {}
    async def on_command_error(self, context: Context, error) -> None:
        retried = error_cooldown.get_bucket(context.message).update_rate_limit()
        if retried:
            current_attemps = 0
            
            try:
                current_attemps = self.error_users_history[context.author.id]
            except:
                pass

            if current_attemps > 1:
                member = context.guild.get_member(context.author.id)
                duration = datetime.timedelta(minutes=5)
                await member.timeout(duration, reason='Spam de comando')
                self.error_users_history[context.author.id] = 0

            else:
                self.error_users_history[context.author.id] = current_attemps + 1
                await context.send(f'Rapaz... {context.author} vo te pegar <:angry:1104539138885177374>',  )
        else:
            await context.send(f'{context.author} Vamo parar de mandar comando q n pode <:frfr:1094799643696701481>',  )
         


load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))
