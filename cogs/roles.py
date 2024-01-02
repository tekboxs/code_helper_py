

import json
import os
from discord.ext import commands
from discord.ext.commands import Context
import discord
from discord import Colour, SelectOption,Interaction


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def getRolesOptions() -> list[SelectOption]:
        role_config = {}
        config_file_path = fr"{os.path.realpath(os.path.dirname(__file__))}/role_config.json"
        with open(config_file_path, encoding="utf8") as file:
            role_config = json.load(file)

        role_list = [SelectOption(label=item['label'], emoji=item['emoji'])
                     for item in role_config['roles']]
        
        return role_list

class RoleDropdownView(discord.ui.View):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.roles = getRolesOptions()
        self.roles_chunks = list(chunk_list(self.roles, 25))
        self.current_chunk = 0
        self.timeout = None
        for i in range(0, len(self.roles_chunks)):
            self.add_dropdown(i)
             

    def add_dropdown(self, chunk_index : int ):
        options = self.roles_chunks[chunk_index]
        dropdown = discord.ui.Select(
            placeholder=f"Menu de Seleção {chunk_index}",
            min_values=1,
            max_values=1,
            options=options)
        
        dropdown.callback = self.select_callback
        self.add_item(dropdown)

    async def select_callback(self, interaction:Interaction):

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


class ProgrammingRoles(commands.Cog, name="ProgrammingRoles"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="choose_role",
        description="Criar menu de cargos.",
    )
    @commands.has_role('Manager')
    async def choose_role(self, context: Context) -> None:
        await context.channel.send("Escolha as ferramentas que melhor representam suas habilidades", view=RoleDropdownView(self.bot))
        await context.send('Menu criado com sucesso ;)', ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(ProgrammingRoles(bot))
