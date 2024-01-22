import discord


class MealButtonView(discord.ui.Button):
    def __init__(self,
                 callback,
                 style=discord.ButtonStyle.blurple,
                 label='Botão',
                 custom_id='btn'):
        super().__init__(
            style=style,
            label=label,
            custom_id=custom_id,
        )

        self.callback = callback
