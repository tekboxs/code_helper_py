import json
import os
from discord.ext import commands
from discord.ext.commands import Context
import discord
from discord import SelectOption, Interaction
from views.button import MealButtonView
from views.dropdown import MealDropdownView
import aiohttp
import aspose.words as aw
import base64
import io
def get_roles_list() -> dict:
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    json_file_path = os.path.join(parent_dir, r"resources/roles/roles_config.json")
    try:
        with open(json_file_path, encoding="utf8") as file:
            roles_list = json.load(file)['roles']
        return roles_list
    except FileNotFoundError:
        print(f"Arquivo JSON não encontrado em {json_file_path}")
        return []


def get_roles_options() -> list[SelectOption]:
    role_config = get_roles_list()

    role_select_list = [SelectOption(label=item, emoji=role_config[item])
                        for item in role_config.keys()]

    return role_select_list


async def create_emoji(ctx: Interaction, emoji_name, image_url):
    # Verifica se o bot tem permissão para gerenciar emojis
    if not ctx.guild.me.guild_permissions.manage_emojis:
        await ctx.send("O bot não tem permissão para gerenciar emojis.")
        return

    # Carrega a imagem
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                await ctx.response.send_message("Falha ao carregar a imagem.")
                return
            svg_data = await resp.read()
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)

    shape = builder.insert_image("cogs/logo_selo.svg")
    shape.get_shape_renderer().save("cogs/logo_selo.png", aw.saving.ImageSaveOptions(aw.SaveFormat.PNG))

    with open('cogs/logo_selo.png', 'rb') as file:
        img_or_gif = io.BytesIO(file.read())
        b_value = img_or_gif.getvalue()
    
        emoji = await ctx.guild.create_custom_emoji(image=b_value, name='name')
        await ctx.send(f'Successfully created emoji')
         
           
         
    # except Exception as e:
    #     await ctx.response.send_message(f"Erro ao converter a imagem: {e}")
    #     return
    # try:
    #     emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=png_data)
    #     await ctx.response.send_message(f"Emoji '{emoji.name}' criado com sucesso.")
    # except discord.HTTPException as e:
    #     await ctx.response.send_message(f"Erro ao criar o emoji: {e}")


class ProgrammingRoles(commands.Cog, name="ProgrammingRoles"):
    async def on_dropdown_select(self, interaction: Interaction) -> None:
        guild = interaction.guild
        role_name = f"{str(interaction.data['values'][0]).capitalize()}"
        role = discord.utils.get(guild.roles, name=role_name)

        await create_emoji(interaction, role_name,
                           'https://github.com/devicons/devicon/blob/master/icons/aarch64/aarch64-original.svg')
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

    async def on_remove_button(self, interaction: discord.Interaction):
        roles_list = get_roles_list()
        member = interaction.user

        if roles_list and member:
            roles_to_remove = [str(role).capitalize() for role in roles_list.keys()]
            roles_to_remove = [discord.utils.get(
                interaction.guild.roles, name=role_name) for role_name in roles_to_remove]
            roles_to_remove = [
                role for role in roles_to_remove if role and role in member.roles]

            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
                await interaction.response.send_message("Cargos removidos com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message("Você não possui nenhum dos cargos a serem removidos.",
                                                        ephemeral=True)
        else:
            await interaction.response.send_message("Erro ao processar a ação.", ephemeral=True)

    def setup_view(self) -> discord.ui.View:
        role_view = MealDropdownView(
            custom_id_prefix='roles_dropwdown_prog',
            options=get_roles_options(),
            callback=self.on_dropdown_select
        )

        role_view.add_item(MealButtonView(
            custom_id='remove_role_drop',
            callback=self.on_remove_button, label='Remover'))
        return role_view

    @commands.hybrid_command(name="choose_role", description="Criar menu de cargos. programação")
    @commands.has_role('Manager')
    async def choose_role(self, context: Context) -> None:
        try:
            await context.channel.send(
                "Escolha as ferramentas que melhor representam suas habilidades",
                view=self.setup_view(),
            )
            await context.send('Menu criado com sucesso ;)', ephemeral=True)
        except Exception as e:
            roles = get_roles_list()
            await context.send(f"{str(e)} {[f'{i} - {item} : {roles[item]}' for i, item in enumerate(roles.keys())]}",
                               ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ProgrammingRoles())

    bot.add_view(ProgrammingRoles().setup_view())
