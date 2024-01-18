import json
import discord
import os

from discord import SelectOption, Interaction
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View

from views.dropdown import MealDropdownView
from views.button import MealButtonView


# Here we name the cog and create a new class for the cog.
class BoostersRoles(commands.Cog, name="boosters"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="boosters_roles",
        description="This commands create a dropdown to boosters select profile colors",
    )
    async def send_booster_roles(self, context: Context) -> None:
        """
        This commands sends a message with boosters dropdown roles

        :param context: The application command context.
        """
        view = self.setup_view()

        await context.send(view=view)

    async def on_dropdown_select(self, interaction: Interaction):
        guild = interaction.guild
        role_name = interaction.data['values'][0]
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            try:
                booster_colors_roles = self.get_role_list()

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

    async def on_remove_button(self, interaction: discord.Interaction):
        roles_list = self.get_role_list()
        member = interaction.user

        if roles_list and member:
            roles_to_remove = [role['name'] for role in roles_list]
            roles_to_remove = [discord.utils.get(
                interaction.guild.roles, name=role_name) for role_name in roles_to_remove]
            roles_to_remove = [
                role for role in roles_to_remove if role and role in member.roles]

            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Cargos removidos com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message("Você não possui nenhum dos cargos a serem removidos.", ephemeral=True)
        else:
            await interaction.response.send_message("Erro ao processar a ação.", ephemeral=True)

    def setup_view(self) -> View:
        role_view = MealDropdownView(
            custom_id_prefix='booster_color_dropdown',
            options=self.get_roles_options(),
            callback=self.on_dropdown_select,
        )

        role_view.add_item(MealButtonView(callback=self.on_remove_button, label='Remover'))
        return role_view

    def get_roles_options(self) -> list[SelectOption]:
        booster_colors_roles = self.get_role_list()
        return [SelectOption(label=role["name"]) for role in booster_colors_roles]

    def get_role_list(self):
        booster_roles_json_path = f"{os.path.dirname(__file__)}/../resources/roles/boosters.json"

        try:
            with open(booster_roles_json_path, encoding="utf8") as file:
                return json.load(file)["roles"]

        except FileNotFoundError:
            print(f"Arquivo JSON não encontrado em {booster_roles_json_path}")
            return []


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(BoostersRoles(bot))
