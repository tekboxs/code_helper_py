import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime
from discord import app_commands


class MemberSinceCog(commands.Cog, name="MemberSince"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="addogmember",
        description="Atribui o cargo 'OG MEMBER' a membros que estão no servidor desde 31/08/2023 ou antes."
    )
    @commands.has_role('Manager')
    @app_commands.describe(dia="Dia de corte", mes="Mes de corte", ano="Ano de corte")
    async def addogmember(self, context: Context, dia: int, mes: int, ano: int):
        """
        Verifica todos os membros do servidor e atribui o cargo 'OG MEMBER' àqueles que estão no servidor desde 31/08/2023 ou antes.
        """

        specified_date = datetime(ano, mes, dia)
        role = discord.utils.get(context.guild.roles, name="OG MEMBER")

        if role is None:
            role = await context.guild.create_role(name="OG MEMBER", color=discord.Colour.from_str("#A84300"))

        await context.send("Cargo 'OG MEMBER' sendo atribuído aos membros elegíveis.", ephemeral=True)
        
        async for member in context.guild.fetch_members(limit=None):
            if member.joined_at is not None and member.joined_at.date() <= specified_date.date():
                asyncio.create_task(member.add_roles(role))
                await asyncio.sleep(0.1)
        else:
            await context.send("Verficação concluida.", ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(MemberSinceCog(bot))
