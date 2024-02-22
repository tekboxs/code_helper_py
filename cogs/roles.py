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


def get_roles_options() -> list[SelectOption]:
    role_config = get_roles_list()

    role_select_list = [SelectOption(label=item['label'], emoji=item['emoji'])
                        for item in role_config]

    return role_select_list


class ProgrammingRoles(commands.Cog, name="ProgrammingRoles"):
    async def on_dropdown_select(self, interaction: Interaction) -> None:
        guild = interaction.guild
        role_name = f"{interaction.data['values'][0]} Dev"
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            try:
                role = await guild.create_role(name=role_name)

            except discord.Forbidden:
                await interaction.response.send_message("Não tenho permissão para criar cargos!", ephemeral=True)
                return

        member = interaction.user

        if role not in member.roles:
            await member.add_roles(role)
            await interaction.response.send_message(f"Cargo {role_name} atribuído com sucesso!", ephemeral=True)
        else:
            await interaction.response.send_message("Você já possui esse cargo!", ephemeral=True)

    async def on_remove_button(self, interaction: discord.Interaction):
        roles_list = get_roles_list()
        member = interaction.user

        if roles_list and member:
            roles_to_remove = [f"{role['label']} Dev" for role in roles_list]
            roles_to_remove = [discord.utils.get(
                interaction.guild.roles, name=role_name) for role_name in roles_to_remove]
            roles_to_remove = [
                role for role in roles_to_remove if role and role in member.roles]

            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Cargos removidos com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message("Você não possui nenhum dos cargos a serem removidos.",
                                                        ephemeral=True)
        else:
            await interaction.response.send_message("Erro ao processar a ação.", ephemeral=True)

    def setup_view(self) -> discord.ui.View:
        role_view = MealDropdownView(
            custom_id_prefix='remove_role_btn',
            options=get_roles_options(),
            callback=self.on_dropdown_select
        )

        role_view.add_item(MealButtonView(callback=self.on_remove_button, label='Remover'))
        return role_view

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
