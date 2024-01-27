import os
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from configs import Configs


class Moderacao(commands.Cog, name="moderacao"):
    def __init__(self, bot) -> None:
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
        # Adiciona uma advertência a um usuário.
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)

        total = await self.bot.database.add_warn(f'{user.name}-{user.id}', context.author.name, reason)
        await context.send(embed=discord.Embed(
            description=f"**{member}** foi advertido por **{context.author}**!\nTotal de advertências: {total}",
            color=0xBEBEFE).add_field(name="Motivo:", value=reason))
        try:
            await member.send(f"Você levou uma advertência em **{context.guild.name}**!\nMotivo: {reason}")
        except:
            await context.send(f"{member.mention}, você foi advertido por **{context.author}**!\nMotivo: {reason}")

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
        await context.channel.purge(limit=amount + 1)
        await context.channel.send(
            embed=discord.Embed(description=f"**{context.author}** deletou **{amount}** mensagens!", color=0xBEBEFE))

    @commands.hybrid_command(name="banirremoto", description="Bane um usuário sem que ele precise estar no servidor.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @app_commands.describe(user_id="O ID do usuário que deve ser banido.",
                           reason="A razão pela qual o usuário deve ser banido.")
    async def banirremoto(self, context: Context, user_id: str, *, reason: str) -> None:
        # Comando para banir um usuário remotamente.
        try:
            if member.guild_permissions.manage_messages:
                owner = context.guild.get_member(Configs().users.tekbox) or await context.guild.fetch_member(
                    Configs().users.tekbox)

                await context.send(
                    content=owner.mention,
                    embed=discord.Embed(description=f"{context.author} tentou banir {member}!", color=0xE02B2B))
                return
            await self.bot.http.ban(user_id, context.guild.id, reason=reason)
            user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
            await context.send(
                embed=discord.Embed(description=f"**{user}** (ID: {user_id}) foi banido por **{context.author}**!",
                                    color=0xBEBEFE).add_field(name="Razão:", value=reason))
        except Exception:
            await context.send(embed=discord.Embed(
                description="Ocorreu um erro ao tentar banir o usuário. Certifique-se de que o ID é um ID existente que pertence a um usuário.",
                color=0xE02B2B))

    @commands.hybrid_command(name="arquivar",
                             description="Arquiva em um arquivo de texto as últimas mensagens com um limite escolhido de mensagens.")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(limit="O limite de mensagens que devem ser arquivadas.")
    async def arquivar(self, context: Context, limit: int = 10) -> None:
        # Comando para arquivar mensagens em um arquivo de texto.
        log_file = f"{context.channel.id}.log"
        with open(log_file, "w", encoding="UTF-8") as file:
            file.write(
                f'Arquivo de mensagens do: #{context.channel} ({context.channel.id}) no servidor "{context.guild}" ({context.guild.id}) em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')
            async for message in context.channel.history(limit=limit, before=context.message):
                attachments = [attachment.url for attachment in message.attachments]
                attachments_text = f"[Arquivo{'s' if len(attachments) >= 2 else ''} Anexado: {', '.join(attachments)}]" if attachments else ""
                file.write(
                    f"{message.created_at.strftime('%d/%m/%Y %H:%M:%S')} {message.author} {message.id}: {message.clean_content} {attachments_text}\n")
        await context.send(file=discord.File(log_file))
        os.remove(log_file)


async def setup(bot) -> None:
    await bot.add_cog(Moderacao(bot))
