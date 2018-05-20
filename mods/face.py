import asyncio
from discord.ext import commands
from PIL import Image, ImageFont, ImageOps, ImageDraw, ImageFilter, ImageEnhance
from io import BytesIO, StringIO

#FACE COMMANDS ARE POSTPONED UNTIL FURTHER NOTICE

class Face():

    def __init__(self,bot):
        self.bot = bot
        self.cursor = self.bot.mysql.cursor
        self.funcs = self.bot.funcs

    async def getFaces(urls):
        faceData = []
        for url in urls:
            headers = {"Ocp-Apim-Subscription-Key":"KEYHERE"}
            data = {"url": url}
            resp = await self.funcs.http_post(url,json=True,headers=headers,data=data)

def setup(bot):
    bot.add_cog(Face(bot))
