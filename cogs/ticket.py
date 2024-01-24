import discord
from discord import Interaction
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View

from views.button import MealButtonView


class TicketCog(commands.Cog, name="ticket"):
    @commands.hybrid_command(name="tkt-i", description="Create buttons")
    @commands.has_role('Manager')
    async def ticket_interactions(self, context: Context) -> None:
        await context.send('Entre em contato com a moderação', view=TicketCog.setup_view())

    @staticmethod
    def setup_view() -> View:
        view = View(timeout=None)
        view.add_item(MealButtonView(callback=TicketCog.ticket_on_click, label='Abrir Ticket', custom_id='tkt-create'))
        return view

    @staticmethod
    async def ticket_on_close(interaction: Interaction) -> None:
        date = datetime.now()
        date_format = "%d-%m-%Y %H:%M:%S"
        formated_date = date.strftime(date_format)
        ticket_closed_name = f"(closed) {interaction.user.name} - {interaction.user.id} - {formated_date}"
        await interaction.channel.edit(name=ticket_closed_name, archived=True)
        await interaction.channel.remove_user(interaction.user)

    @staticmethod
    def setup_close_view() -> View:
        remove_button_view = View(timeout=None)
        remove_button_view.add_item(MealButtonView(
            TicketCog.ticket_on_close,
            label='Fechar Ticket',
            style=discord.ButtonStyle.red,
            custom_id='tkt-delete'))
        return remove_button_view

    @staticmethod
    async def ticket_on_click(interaction: Interaction) -> None:

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(
                        content=f"Você já tem um atendimento em andamento!",
                        ephemeral=True)
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_response(content=f"Você já tem um atendimento em andamento!",
                                                             view=None)
                    return

        if ticket is not None:
            await ticket.edit(archived=False, locked=False)
            await ticket.edit(name=f"{interaction.user.name} - {interaction.user.id}",
                              auto_archive_duration=10080,
                              invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} - {interaction.user.id}",
                                                             auto_archive_duration=10080)
            await ticket.edit(invitable=False)

        await interaction.response.send_message(f"Seu Ticket foi criado! {ticket.mention}", ephemeral=True)

        await ticket.send(
            f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e "
            f"aguarde até que um membro da equipe responda.",
            view=TicketCog.setup_close_view()
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TicketCog())
    bot.add_view(TicketCog.setup_view())
    bot.add_view(TicketCog.setup_close_view())
