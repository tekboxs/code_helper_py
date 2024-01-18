import discord
from discord import Interaction
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View

from views.button import MealButtonView


async def ticket_on_click(interaction: Interaction) -> None:

    ticket = None
    for thread in interaction.channel.threads:
        if f"{interaction.user.id}" in thread.name:
            if thread.archived:
                ticket = thread
            else:
                await interaction.channel.send(
                    content=f"Você já tem um atendimento em andamento!")
                return

    async for thread in interaction.channel.archived_threads(private=True):
        if f"{interaction.user.id}" in thread.name:
            if thread.archived:
                ticket = thread
            else:
                await interaction.edit_original_response(content=f"Você já tem um atendimento em andamento!", view=None)
                return

    if ticket is not None:
        await ticket.edit(archived=False, locked=False)
        await ticket.edit(name=f"{interaction.user.name} ({interaction.user.id})", auto_archive_duration=10080,
                          invitable=False)
    else:
        ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})",
                                                         auto_archive_duration=10080)
        await ticket.edit(invitable=False)

    await interaction.channel.send(f"Criei um ticket para você! {ticket.mention}")
    await ticket.send(
        f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e "
        f"aguarde até que um atendente responda.")


class TicketCog(commands.Cog, name="ticket"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="tkt-i", description="Create buttons")
    @commands.has_role('Manager')
    async def ticket_interactions(self, context: Context) -> None:
        view = View()
        view.add_item(MealButtonView(callback=ticket_on_click, label='Abrir Ticket'))
        await context.send('asd', view=view)


async def setup(bot) -> None:
    await bot.add_cog(TicketCog(bot))
