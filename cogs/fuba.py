import random
import discord
from discord.ext import commands
from discord.ext.commands import Context

class BoloDeFuba(commands.Cog, name="BoloDeFubá"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="receita", description="Obtenha uma receita aleatória de bolo de fubá.")
    async def receita(self, context: Context) -> None:
        """
        Envia uma receita aleatória de bolo de fubá para o usuário.

        :param context: O contexto do comando híbrido.
        """
        receitas = [
            "**Bolo de Fubá Simples**\nIngredientes: fubá, farinha, ovos, açúcar, fermento e leite.\nInstruções: Misture os ingredientes secos, adicione os ovos e o leite, asse por 40 minutos.",
            "**Bolo de Fubá Cremoso**\nIngredientes: fubá, queijo ralado, ovos, açúcar, leite, margarina.\nInstruções: Bata tudo no liquidificador, asse em forma untada por 45 minutos."
        ]
        escolha = random.choice(receitas)
        await context.send(embed=discord.Embed(description=escolha, color=0xF1C232))

    @commands.hybrid_command(name="curiosidade", description="Obtenha uma curiosidade sobre bolo de fubá.")
    async def curiosidade(self, context: Context) -> None:
        """
        Envia uma curiosidade aleatória sobre bolo de fubá.

        :param context: O contexto do comando híbrido.
        """
        curiosidades = [
            "Você sabia que o bolo de fubá é uma receita tradicional brasileira, com origens na culinária dos escravos africanos?",
            "O bolo de fubá é perfeito para o café da manhã ou lanche da tarde, combinando bem com um cafézinho."
        ]
        escolha = random.choice(curiosidades)
        await context.send(embed=discord.Embed(description=escolha, color=0xF1C232))

    @commands.hybrid_command(name="enfeitar", description="Enfeite seu bolo de fubá virtual.")
    async def enfeitar(self, context: Context) -> None:
        """
        Oferece opções para enfeitar um bolo de fubá virtual.

        :param context: O contexto do comando híbrido.
        """
        enfeites = ["coco ralado", "goiabada derretida", "canela em pó", "calda de chocolate"]
        escolha = random.choice(enfeites)
        await context.send(embed=discord.Embed(description=f"Você enfeitou seu bolo de fubá com {escolha}! Delicioso!", color=0xF1C232))

    @commands.hybrid_command(name="avaliar", description="Avalie um bolo de fubá.")
    async def avaliar(self, context: Context) -> None:
        """
        Permite ao usuário avaliar um bolo de fubá numa escala de 1 a 5.

        :param context: O contexto do comando híbrido.
        """
        avaliacao = random.randint(1, 5)
        await context.send(embed=discord.Embed(description=f"Você avaliou o bolo de fubá com uma nota {avaliacao} de 5!", color=0xF1C232))

async def setup(bot) -> None:
    await bot.add_cog(BoloDeFuba(bot))
