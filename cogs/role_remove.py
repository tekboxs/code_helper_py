import os
import discord
from discord.ext import commands
from discord.ui import Button
import json

class RemoveRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_roles_list(self):
        # Substitua este caminho pelo caminho real do seu arquivo JSON
        
        json_file_path = fr"{os.path.realpath(os.path.dirname(__file__))}/role_config.json"
        try:
            with open(json_file_path, encoding="utf8") as file:
                roles_list = json.load(file)
            return roles_list
        except FileNotFoundError:
            print(f"Arquivo JSON não encontrado em {json_file_path}")
            return []

    async def on_button_click(self, interaction):
        roles_list = self.get_roles_list()['roles']
        member = interaction.user

        if roles_list and member:
            roles_to_remove = [f"{role['label']} Dev" for role in roles_list]
            roles_to_remove = [discord.utils.get(interaction.guild.roles, name=role_name) for role_name in roles_to_remove]
            roles_to_remove = [role for role in roles_to_remove if role and role in member.roles]

            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Cargos removidos com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message("Você não possui nenhum dos cargos a serem removidos.", ephemeral=True)
        else:
            await interaction.response.send_message("Erro ao processar a ação.", ephemeral=True)

    @commands.command()
    async def remove_roles_button(self, ctx):
        view = discord.ui.View()
        button = Button(style=discord.ButtonStyle.primary, label="Remover Cargos", custom_id="remove_roles_button")
        button.callback = self.on_button_click
        view.add_item(button)

        await ctx.send("Clique no botão abaixo para remover os cargos:", view=view)

async def setup(bot):
    await bot.add_cog(RemoveRolesCog(bot))
