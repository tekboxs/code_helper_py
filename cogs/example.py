import discord
from discord.ext import commands
from discord.ui import View, Button
from functools import partial

class GenericButtonView(View):
    def __init__(self, callback, *args, **kwargs):
        super().__init__()
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def add_button(self):
        button = Button(style=discord.ButtonStyle.primary, label="Clique aqui!", custom_id="generic_button")
        button.callback = partial(self.on_button_click, *self.args, **self.kwargs)
        self.add_item(button)

    async def on_button_click(self, button, interaction, *args, **kwargs):
        await self.callback(interaction, *args, **kwargs)

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_generic_button_click(self, interaction, argument):
        await interaction.response.send_message(f"Botão genérico clicado com argumento: {argument}")

    @commands.command()
    async def example_command(self, ctx):
        view = GenericButtonView(self.on_generic_button_click, argument="Exemplo")
        view.add_button()
        await ctx.send("Clique no botão abaixo:", view=view)
async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
