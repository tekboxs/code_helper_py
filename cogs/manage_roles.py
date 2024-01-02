import discord
from discord.ext.commands import Context
from discord.ext import commands 
from discord.ui import Button

class GenericButtonView(discord.ui.View):
    def __init__(self, callback, label, *args, **kwargs):
        super().__init__(timeout=None)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.timeout = None
        button = Button(style=discord.ButtonStyle.primary, label=label, custom_id="generic_button")
        button.callback = self.on_button_click
        self.add_item(button)
    
    def add_button(self):
        button = Button(style=discord.ButtonStyle.primary, label="Clique aqui!", custom_id="generic_button")
        button.callback = self.on_button_click
        self.add_item(button)

    async def on_button_click(self, interaction):
        await self.callback(interaction, *self.args, **self.kwargs)

 

class ManageRolesCog(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_roles_options(self, guild):
        roles_list = [{"label": role.name, "value": role.id} for role in guild.roles]
        return roles_list

    async def delete_role(interaction:discord.Interaction, role_id: int):
      role = discord.utils.get(interaction.guild.roles, id=role_id)
      await role.delete()
      interaction.channel.send(f'{role.name} foi jogar no vasco')
      
       

    @commands.command()
    @commands.has_role('Manager')
    async def list_roles(self, ctx: Context):
        roles_options = self.get_roles_options(ctx.guild)

        if not roles_options:
            await ctx.send("Não há cargos para exibir.")
            return
        i=0
        for item in roles_options:
         message_content = item['label']
         await ctx.channel.send(content=message_content, view=GenericButtonView(self.delete_role(item['value']), 'Deletar'))
         i+=1
         if i == 4:
            break

          
async def setup(bot):
    await bot.add_cog(ManageRolesCog(bot))
