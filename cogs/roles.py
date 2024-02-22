import asyncio.tasks
import json
import os

import aiohttp
import discord
from discord import SelectOption, Interaction, Emoji, Role
from discord.ext import commands
from discord.ext.commands import Context

from views.button import MealButtonView
from views.dropdown import MealDropdownView


class Roles(commands.Cog, name="Roles"):
    def __init__(self):
        self.config: {} = None

        self.images: dict[str, bytes] = {}
        self.emojis: dict[str, Emoji] = {}
        self.roles: dict[str, Role] = {}

        asyncio.create_task(self.get_config())

    async def get_config(self) -> None:
        try:
            path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "roles_config.json")
            with open(path, encoding="utf8") as file:
                self.config = json.load(file)

        except FileNotFoundError:
            print(f"Arquivo JSON não encontrado em {path}")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://raw.githubusercontent.com/devicons/devicon/master/devicon.json") as response:
                for icon in await response.json(content_type="text/plain"):
                    if "language" in icon["tags"] and not icon["name"] in self.config["ignore"]:
                        kind = "original"

                        if icon["name"] in self.config["icon"]:
                            kind = self.config["icon"][icon["name"]]

                        async with session.get(
                                f'https://raw.githubusercontent.com/devicons/devicon/master/icons/{icon["name"]}'
                                f'/{icon["name"]}-{kind}.svg') as svg:
                            self.images[icon["name"]] = bytes(await svg.text(), "UTF-8")

    def prettify(self, name: str) -> str:
        if name in self.config.prettify:
            return self.config.prettify[name]

        return name.capitalize()

    def options(self) -> list[SelectOption]:
        return [SelectOption(label=self.prettify(name), emoji=emoji) for name, emoji in self.emojis]

    @commands.has_permissions(manage_roles=True, manage_guild=True)
    async def setup(self, interaction: Interaction) -> None:
        for role in self.roles:
            if role not in interaction.guild.emojis:
                self.emojis[self.prettify(role)] = await interaction.guild.create_custom_emoji(
                    name=role,
                    image=self.images[role],
                    reason="emoji for role was not found"
                )

            if role not in interaction.guild.roles:
                self.roles[self.prettify(role)] = await interaction.guild.create_role(
                    name=self.prettify(role),
                    display_icon=self.emojis[role].name,
                    reason="role for role was not found"
                )

    async def on_dropdown_select(self, interaction: Interaction) -> None:
        roles = []

        for value in interaction.data["values"]:
            role = self.roles[value]

            if role is None:
                return await interaction.response.send_message("role was not found, ask an administrator to resync "
                                                               "the guild!", ephemeral=True)
            roles.append(role)

            if role in interaction.user.roles:
                return await interaction.response.send_message("Você já possui esse cargo!", ephemeral=True)



    @commands.hybrid_command(name="choose_role", description="Criar menu de cargos.")
    @commands.has_role('Manager')
    async def choose_role(self, context: Context) -> None:

        await context.channel.send(
            "Escolha as ferramentas que melhor representam suas habilidades",
            view=self.setup_view(),
        )
        await context.send('Menu criado com sucesso ;)', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ProgrammingRoles())

    bot.add_view(ProgrammingRoles().setup_view())
