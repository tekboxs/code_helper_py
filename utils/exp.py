import discord
from discord.ext import commands
from discord.ext.commands import Context
import vacefron
import math
import random


def remove_duplicates(duplicated_message):
    return ''.join(sorted(set(duplicated_message.lower())))


class XpCog(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.max_typing_speed = 50
    last_message = {}
    message_cooldown = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

    async def compute_xp(self, message: discord.Message):

        if len(remove_duplicates(message.content)) < 5:
            return
        retry_after = self.message_cooldown.get_bucket(message).update_rate_limit()
        if retry_after:
            return

        if message.author in self.last_message.keys():
            total_words = message.content.split(" ")
            normal_words = (item for item in total_words if len(item) > 2)
            elapsed_time = (message.created_at - self.last_message[message.author]["time"] ).total_seconds()

            typing_speed = (len(list(normal_words)) / int(elapsed_time)) * 60
            await message.reply(f"typing speed:{typing_speed}")
            await message.reply(f"elapsed time:{elapsed_time}")
            if typing_speed > self.max_typing_speed:
                await message.reply("Você está digitando muito rápido. Por favor, desacelere.")
                return
            if self.last_message[message.author]["content"] == message.content:
                await message.reply("Repetida")
                return
            self.last_message[message.author] = {"content": message.content, "time": message.created_at}
        else:
            self.last_message[message.author] = {"content": message.content, "time": message.created_at}

        await message.reply(remove_duplicates(message.content))
            

