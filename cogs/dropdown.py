import discord
from discord import SelectOption
from discord.ext import commands
from discord.ui import Select
import json

class DropdownCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def chunk_list(self, lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    def get_roles_options(self):
        # Substitua esta lista pela sua lista real de opções
        roles_list = [
            {"label": "Python", "value": "python", "emoji": "🐍"},
            # Adicione mais elementos conforme necessário
        ]
        role_options = [SelectOption(label=item['label'], value=item['value'], emoji=item['emoji']) for item in roles_list]
        return role_options

    def create_dropdown_view(self, roles_options):
        class RoleDropdownView(discord.ui.View):
            def __init__(self, roles_options):
                super().__init__()
                self.roles_options = roles_options
                self.roles_chunks = list(self.chunk_list(self.roles_options, 25))
                self.current_chunk = 0

                self.add_dropdown()

            def add_dropdown(self):
                options = self.roles_chunks[self.current_chunk]
                dropdown = Select(
                    placeholder="Escolha uma linguagem de programação...",
                    min_values=1,
                    max_values=1,
                    options=options,
                    custom_id=f"role_dropdown_{self.current_chunk}"
                )
                dropdown.callback = self.select_callback
                self.add_item(dropdown)

            async def select_callback(self, select, interaction):
                selected_value = select.values[0]
                await interaction.response.send_message(f"Você escolheu: {selected_value}", ephemeral=True)

            async def on_dropdown(self, interaction):
                self.current_chunk += 1

                if self.current_chunk < len(self.roles_chunks):
                    # Adicione o próximo dropdown
                    self.add_dropdown()
                    await interaction.edit_original_message(view=self)
                else:
                    # Remova a visão após todos os dropdowns terem sido usados
                    await interaction.response.defer(edit_origin=True)
                    self.stop()

        return RoleDropdownView(roles_options)

    @commands.hybrid_command(
        name="dropdown",
        description="---",
    )
    async def roles_command(self, ctx):
        roles_options = self.get_roles_options()
        dropdown_view = self.create_dropdown_view(roles_options)
        await ctx.send("Escolha uma opção:", view=dropdown_view)

async def setup(bot):
    await bot.add_cog(DropdownCog(bot))