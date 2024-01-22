import json
import discord
import os

from discord import SelectOption, Interaction
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View

from views.dropdown import MealDropdownView
from views.button import MealButtonView


class BoostersRoles(commands.Cog, name="boosters"):
    @commands.hybrid_command(
        name="boosters_roles",
        description="This commands create a dropdown to boosters select profile colors",
    )
    @commands.has_role('Manager')
    async def send_booster_roles(self, context: Context) -> None:
        """
        This commands sends a message with boosters dropdown roles

        :param context: The application command context.
        """
        view = setup_view()

        await context.send(view=view)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BoostersRoles())
    bot.add_view(setup_view())


def get_role_list():
    booster_roles_json_path = f"{os.path.dirname(__file__)}/../resources/roles/boosters.json"

    try:
        with open(booster_roles_json_path, encoding="utf8") as file:
            return json.load(file)["roles"]

    except FileNotFoundError:
        print(f"Arquivo JSON não encontrado em {booster_roles_json_path}")
        return []


def get_roles_options() -> list[SelectOption]:
    booster_colors_roles = get_role_list()
    return [SelectOption(label=role["name"], emoji=role['emoji']) for role in booster_colors_roles]


async def on_remove_button(interaction: discord.Interaction):
    roles_list = get_role_list()
    member = interaction.user

    if roles_list and member:
        roles_to_remove = [role['name'] for role in roles_list]
        roles_to_remove = [discord.utils.get(
            interaction.guild.roles, name=role_name) for role_name in roles_to_remove]
        roles_to_remove = [
            role for role in roles_to_remove if role and role in member.roles]

        await member.remove_roles(*roles_to_remove)
        await interaction.response.send_message("Cargos removidos com sucesso!", ephemeral=True)
        return

    await interaction.response.send_message("Erro ao processar a ação.", ephemeral=True)


async def on_dropdown_select(interaction: Interaction):
    guild = interaction.guild
    role_name = interaction.data['values'][0]
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        try:
            booster_colors_roles = get_role_list()

            for color in booster_colors_roles:
                if color["name"] == role_name:
                    color_code = color["color"]

            role = await guild.create_role(name=role_name, color=discord.Colour.from_str(color_code))

        except discord.Forbidden:
            await interaction.response.send_message("Não tenho permissão para criar cargos!", ephemeral=True)
            return

    member = interaction.user

    if role not in member.roles:
        await member.add_roles(role)
        await interaction.response.send_message(f"Cargo {role_name} atribuído com sucesso!", ephemeral=True)
    else:
        await interaction.response.send_message("Você já possui esse cargo!", ephemeral=True)


def setup_view() -> View:
    role_view = MealDropdownView(
        custom_id_prefix='booster_color_dropdown',
        options=get_roles_options(),
        callback=on_dropdown_select,
    )

    role_view.add_item(MealButtonView(callback=on_remove_button, label='Remover'))
    return role_view
