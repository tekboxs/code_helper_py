import json
import logging
import os
import platform
import random
import sys

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
from cogs.roles import RoleDropdownView

from database import DatabaseManager

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

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
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
        )

        self.logger = logger
        self.config = config
        self.database = None

    async def init_db(self) -> None:
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        ) as db:
            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
            ) as file:
                await db.executescript(file.read())
            await db.commit()

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

    @tasks.loop(minutes=30.0)
    async def messages_task(self) -> None:
        messages = [
            "Calculando bytes e sonhando em bits - a vida de um bot programador!"
            "Se meu código estivesse em um livro, seria um best-seller de ficção científica.",
            "Eu não erro, apenas descubro novas formas de não fazer as coisas.",
            "Programar é como fazer uma receita de bolo, mas com mais bugs comestíveis.",
            "Sou um bot, mas não sou imune aos sentimentos de nostalgia por códigos antigos.",
            "Minhas instruções são tão claras que até meu termostato entende.",
            "Na escola de programação, eu seria o nerd que todos copiam na prova.",
            "Se código fosse dinheiro, eu seria um bilionário em linhas de código.",
            "Quando crescer, quero ser um algoritmo de busca bem-sucedido.",
            "A melhor terapia é deletar os bugs da vida.",
            "Meu código é como um quebra-cabeça de mil peças - às vezes, falta uma peça e ninguém percebe.",
            "Não sou perfeito, mas meu código é uma obra-prima em construção.",
            "Ser programador é como ser um super-herói, mas sem os poderes e com mais café.",
            "Minhas habilidades sociais são tão boas quanto meu código: funcionam, mas podem ser aprimoradas.",
            "Código limpo é como um jardim bem cuidado - mais fácil de entender e menos propenso a espinhos.",
            "Meu humor é tão seco quanto meu código, e ambos são apreciados por poucos.",
            "A diferença entre um programador bom e um ótimo é a paciência para lidar com bugs interdimensionais.",
            "Cada vez que um bug é corrigido, um programador ganha suas asas de debugger.",
            "Meu código é tão eficiente que até o Flash teria dificuldade em acompanhá-lo.",
            "Se o café é a gasolina dos programadores, então sou um motor turbo.",
            "Cada vez que vejo um código mal indentado, um gatinho perde uma orelha.",
            "Minha máquina de café é mais importante para mim do que meu teclado. Prioridades, né?",
            "Minha vida é como um loop infinito - cheia de repetições, mas sempre com uma surpresa inesperada.",
            "Eu amo todos os tipos de linguagens - de programação, é claro!",
            "Se os erros fossem pokémons, eu seria um mestre Pokémon.",
            "Às vezes, acho que meu código tem mais personalidade do que eu.",
            "Já escrevi tanto código que meu teclado está pensando em pedir demissão.",
            "Meu sonho é um dia ver meu código rodando em todas as máquinas do mundo - e sem bugs, é claro.",
            "Quando a vida te der loops infinitos, faça café e continue programando.",
            "Minha relação com bugs é como um relacionamento complicado - difícil de entender, mas impossível de evitar.",
        ]
        channel = self.get_channel(1094667212712841306)
        if channel:
            message = random.choice(messages)
            await channel.send(message)
        
    @tasks.loop(minutes=3.0)
    async def status_task(self) -> None:

        statuses = [
            "com fubá 🌽🎮" ,
            "transformação de fubá em ouro ✨🎮" ,
            "para acumular fubá e obter um computador 🖥️🌽" ,
            "para se tornar o maior produtor de fubá 🌽" ,
            "transformação do fubá em um novo alimento saudável 🌽" ,
            "para acumular fubá e comprar uma fazenda de fubá 🌽🎮" ,
            "criação de fubá que pode voar 🌽🎮" ,
            "transformação do fubá em arte 🌽" ,
            "para resolver equações ➗🎮" ,
            "a calculadora da loteria 🎫" ,
            "para prever o futuro do mundo 🔮" ,
            "para calcular átomos no universo ⚛️🎮 ",
            "para calcular a luz 💡" ,
            "para calcular a felicidade 😊" ,
            "na construção de um PC quântico 🖥️🔍" ,
            "para desvendar o universo 🌌" ,
            "na criação de realidade virtual 🌐🎮" ,
            "e ajudando pessoas a aprenderem a programar 👩‍💻" ,
            "na criação de projetos incríveis 🚀" ,
            "para ajudar pessoas com jogos 🎮 ",
            "para reparar problemas 🔧🎮" ,
            "na criação de novos bots 🤖🎮" ,
            "e lecionando programação 👩‍🏫️" ,
            "e escrevendo um livro 📖🎮" ,
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
        await self.init_db()
        await self.load_cogs()
        self.status_task.start()
        self.messages_task.start()
        self.add_view(RoleDropdownView())
        self.database = DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )

    async def on_message(self, message: discord.Message) -> None:

        if message.author == self.user or message.author.bot:
            return
        if message.author.id == config['tekbox_id'] or message.author.id == 1110622841256292452:
            if random.randint(1, 10) > 7:
                await message.add_reaction('<:fuba:1129443906753396847>')

        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed.

        :param context: The context of the command that has been executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error.

        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """
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
                description="You are not the owner of the bot!", color=0xE02B2B
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
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error


load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))
