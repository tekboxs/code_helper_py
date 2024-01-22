from typing import Callable, Any, Coroutine
import discord


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


class MealDropdownView(discord.ui.View):
    """
    Create a generic corn meal dropdown view

    Parameters
    -----------
    callback > should have argument interaction: Interaction
    """

    def __init__(self,
                 custom_id_prefix: str,
                 options: list[discord.SelectOption],
                 callback: Callable[[discord.Interaction], Coroutine[Any, Any, None]],
                 persistent=True,
                 max_values=1,
                 min_values=1,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_id_prefix = custom_id_prefix
        self.options = options

        self.options_chunks = list(chunk_list(self.options, 25))

        self.max_values = max_values
        self.min_values = min_values

        if persistent:
            self.timeout = None

        self.callback = callback

        for i in range(0, len(self.options_chunks)):
            self.create_dropdown(i)

    def create_dropdown(self, index: int):
        create_options = self.options_chunks[index]
        dropdown = discord.ui.Select(
            placeholder=f"Menu de Seleção {index + 1}",
            min_values=self.min_values,
            max_values=self.max_values,
            options=create_options,
            custom_id=f'{self.custom_id_prefix}:{index + 1}'
        )

        dropdown.callback = self.callback
        self.add_item(dropdown)
