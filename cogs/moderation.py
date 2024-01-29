import asyncio
import os
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from configs import Configs


class Moderacao(commands.Cog, name="moderacao"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="apelido", description="Altera o apelido de um usuário no servidor.")
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @app_commands.describe(user="O usuário que deve ter um novo apelido.",
                           nickname="O novo apelido que deve ser definido.")
    async def apelido(self, context: Context, user: discord.User, *, nickname: str = None) -> None:
        # Comando para alterar o apelido de um usuário.
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        try:
            await member.edit(nick=nickname)
            await context.send(
                embed=discord.Embed(description=f"O novo apelido de **{member}** é **{nickname}**!", color=0xBEBEFE))
        except:
            await context.send(embed=discord.Embed(
                description="Ocorreu um erro ao tentar alterar o apelido do usuário",
                color=0xE02B2B))

    @commands.hybrid_command(name="banir", description="Bane um usuário do servidor.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @app_commands.describe(user="O usuário que deve ser banido.", reason="A razão pela qual o usuário deve ser banido.")
    async def banir(self, context: Context, user: discord.User, *, reason: str) -> None:
        # Comando para banir um usuário do servidor.
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        try:
            if member.guild_permissions.manage_messages:
                owner = context.guild.get_member(Configs().users.tekbox) or await context.guild.fetch_member(
                    Configs().users.tekbox)

                await context.send(
                    content=owner.mention,
                    embed=discord.Embed(description=f"{context.author} tentou banir {member}!", color=0xE02B2B))
            else:
                await context.send(embed=discord.Embed(description=f"**{member}** foi banido por **{context.author}**!",
                                                       color=0xBEBEFE).add_field(name="Razão:", value=reason))
                await member.send(
                    f"Você foi banido por **{context.author}** de **{context.guild.name}**!\nRazão: {reason}")
                await member.ban(reason=reason)
        except Exception as e:
            await context.send(embed=discord.Embed(title="Erro!",
                                                   description=f"{e} Ocorreu um erro ao tentar banir o usuário.",
                                                   color=0xE02B2B))

    @commands.hybrid_group(name="advertencia", description="Gerencia advertências de um usuário no servidor.")
    @commands.has_permissions(manage_messages=True)
    async def advertencia(self, context: Context) -> None:
        # Grupo de comandos para gerenciar advertências de usuários.
        if context.invoked_subcommand is None:
            await context.send(embed=discord.Embed(
                description="Especifique um subcomando.",
                color=0xE02B2B))

    @advertencia.command(name="adicionar", description="Adiciona uma advertência a um usuário no servidor.")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(user="O usuário que deve ser advertido.",
                           reason="A razão pela qual o usuário deve ser advertido.")
    async def advertencia_adicionar(self, context: Context, user: discord.User, *,
                                    reason: str) -> None:
        await context.interaction.response.defer()

        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)

        total = await self.bot.database.add_warn(f'{user.name}-{user.id}', context.author.name, reason)
        
             
        try:
            await member.send(f"Você levou uma advertência em **{context.guild.name}**!\nMotivo: {reason}")
        except:
            channel = context.guild.get_channel(Configs().interno.geral)
            await channel.send(f"{member.mention}, você foi advertido por **{context.author}**!\nMotivo: {reason}")

        await context.interaction.followup.send( f"**{member}** foi advertido por **{context.author}**!\nTotal de advertências: {total}")
             

    @advertencia.command(name="remover", description="Remove uma advertência de um usuário no servidor.")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(user="O usuário que deve ter sua advertência removida.",
                           warn_id="O ID da advertência que deve ser removida.")
    async def advertencia_remover(self, context: Context, user: discord.User, warn_id: int) -> None:
        # Remove uma advertência de um usuário.
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        total = await self.bot.database.remove_warn(warn_id, f"{user.name}-{user.id}")

        await context.send(embed=discord.Embed(
            description=f"Removi a advertência **#{warn_id}** de **{member}**!\nTotal de advertências: {total}",
            color=0xBEBEFE))

    @advertencia.command(name="listar", description="Mostra as advertências de um usuário no servidor.")
    @commands.has_guild_permissions(manage_messages=True)
    @app_commands.describe(user="O usuário que você deseja obter as advertências.")
    async def advertencia_listar(self, context: Context, user: discord.User) -> None:
        # Mostra as advertências de um usuário.
        warnings_list = await self.bot.database.list_warn(f"{user.name}-{user.id}")
        embed = discord.Embed(title=f"Advertências de {user}", color=0xBEBEFE)
        description = "Esse usuário não tem advertências." if len(warnings_list) == 0 else "".join(
            f"• Por {warning['author']}\n**{warning['motivo']}**\n{warning['data']} - ID #{warnings_list.index(warning)}\n\n" for
            warning in warnings_list)
        embed.description = description
        await context.send(embed=embed)

    @commands.hybrid_command(name="limpar", description="Deleta uma quantidade de mensagens.")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @app_commands.describe(amount="A quantidade de mensagens que devem ser deletadas.")
    async def limpar(self, context: Context, amount: int) -> None:
        # Comando para deletar mensagens.
        await context.channel.send(
            embed=discord.Embed(description=f"**{context.author}** Removendo **{amount}** mensagens!", color=0xBEBEFE,
                                ))
        
        asyncio.create_task(context.channel.purge(limit=amount + 1))


async def setup(bot) -> None:
    await bot.add_cog(Moderacao(bot))
