import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime

class MemberSinceCommand(commands.Cog, name="MemberSince"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="addogmember", help="Atribui o cargo 'OG MEMBER' a membros que estão no servidor desde 31/08/2023 ou antes.")
    @commands.has_role('Manager')
    async def addogmember(self, ctx: Context):
        """
        Verifica todos os membros do servidor e atribui o cargo 'OG MEMBER' àqueles que estão no servidor desde 31/08/2023 ou antes.

        :param ctx: O contexto do comando.
        """

        specified_date = datetime(2023, 8, 31)
        role = discord.utils.get(ctx.guild.roles, name="OG MEMBER")

        if role is None:
            await ctx.send("Cargo 'OG MEMBER' não encontrado no servidor.")
            return

        # Paginação: processar membros em grupos de 200
        members = ctx.guild.members
        page_size = 200

        for i in range(0, len(members), page_size):
            # Pegando uma "página" de membros
            page_members = members[i:i + page_size]

            for member in page_members:
                if member.joined_at is not None and member.joined_at.date() <= specified_date.date():
                    await member.add_roles(role)

            # Enviando feedback para o canal após processar cada página
            await ctx.send(f"Processando membros {i+1} até {min(i + page_size, len(members))}...")

        await ctx.send("Cargo 'OG MEMBER' atribuído aos membros elegíveis.")

async def setup(bot) -> None:
    await bot.add_cog(MemberSinceCommand(bot))


