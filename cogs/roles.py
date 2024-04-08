import asyncio.tasks
import json
import os

import aiohttp
import discord
import pyvips
from discord import SelectOption, Interaction, Emoji, Role, Guild
from discord.ext import commands
from discord.ext.commands import Context

from views.button import MealButtonView
from views.dropdown import MealDropdownView


class Roles(commands.Cog, name="Roles"):
    def __init__(self):
        self.config: {} = None
        self.images: dict[str, bytes] = {}

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
                            if svg.status != 200:
                                print("returned",
                                      f'https://raw.githubusercontent.com/devicons/devicon/master/icons/{icon["name"]}'
                                      f'/{icon["name"]}-{kind}.svg')
                                return

                            self.images[icon["name"]] = pyvips.Image.new_from_buffer(
                                bytes(await svg.text(), "UTF-8"),
                                "",
                                access="sequential"
                            ).write_to_buffer(".png")

    def prettify(self, name: str) -> str:
        if name in self.config["prettify"]:
            return self.config["prettify"][name]
        else:
            try:
                i = name.rindex("sharp")
                return name.capitalize()[:i] + "#"
            except ValueError:
                pass

            try:
                i = name.rindex("script")
                return name.capitalize()[:i] + "Script"
            except ValueError:
                pass

        return name.capitalize()

    def add_pl(self, name: str) -> str:
        if len(name) == 1:
            name += "pl"

        return name

    def options(self, guild: Guild) -> list[SelectOption]:
        return [SelectOption(
            label=self.prettify(name),
            emoji=discord.utils.get(guild.emojis, name=name)
        ) for name in self.images]

    async def setup(self, context: Context) -> None:
        for name in self.images:
            emoji = discord.utils.get(context.guild.emojis, name=name)

            if emoji is None:
                emoji = await context.guild.create_custom_emoji(
                    name=self.add_pl(name),
                    image=self.images[name],
                    reason="emoji for role was not found"
                )

            emoji_name = None
            if context.guild.premium_tier >= 1:
                emoji_name = emoji.name

            if discord.utils.get(context.guild.roles, name=name) is None:
                await context.guild.create_role(
                    name=self.prettify(name),
                    display_icon=emoji_name,
                    reason="role was not found"
                )

    async def on_dropdown_select(self, interaction: Interaction) -> None:
        role = discord.utils.get(interaction.guild.roles, name=interaction.data["values"][0])
        if role is None:
            return await interaction.response.send_message("role was not found, ask an administrator to resync "
                                                           "the guild!", ephemeral=True)
        if role in interaction.user.roles:
            return await interaction.response.send_message("Você já possui esse cargo!", ephemeral=True)

        await interaction.user.add_roles(role)
        return await interaction.response.send_message(f"Cargo ${role.name} atribuído com sucesso!", ephemeral=True)

    async def on_dropdown_remove(self, interaction: Interaction) -> None:
        await interaction.user.remove_roles(*[discord.utils.get(
            interaction.guild.roles, name=self.prettify(name)) for name in self.images])
        return await interaction.response.send_message(f"Cargos removidos com sucesso!", ephemeral=True)

    def view(self, guild: Guild) -> discord.ui.View:
        return MealDropdownView(
            custom_id_prefix="remove_role_btn",
            options=self.options(guild),
            callback=self.on_dropdown_select,
        ).add_item(MealButtonView(callback=self.on_dropdown_remove, label="Remover"))

    @commands.hybrid_command(name="choose_roles", description="Criar menu de cargos.")
    @commands.has_role("Manager")
    async def choose(self, context: Context) -> None:
        await context.channel.send(
            "Escolha as ferramentas que melhor representam suas habilidades",
            view=self.view(context.guild),
        )
        await context.channel.send('Menu criado com sucesso ;)', )

    @commands.hybrid_command("sync_roles", description="synchronize roles in the guild.")
    @commands.has_role("Manager")
    async def sync(self, context: Context) -> None:
        await self.setup(context)
        await context.channel.send(f"Roles {self.images.keys()} synchronized.")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Roles())

    bot.add_view(Roles().view(None))
