import asyncio
import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageOps, ImageDraw, ImageFilter, ImageEnhance
from io import BytesIO, StringIO
from utils import MSFace
from utils import checks
import traceback

#FACE COMMANDS ARE POSTPONED UNTIL FURTHER NOTICE

class Face():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor
		self.funcs = self.bot.funcs
		self.face = MSFace.MSFace(key=self.bot.bot_prefs["face_token"])
		self.get_images = self.bot.get_images


	@commands.command()
	@checks.is_bot_owner()
	async def getfaces(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls,limit=1)
			if images:
				for url in images:
					faces = await self.face.detect(url,landmarks=False)
					if "error" in faces:
						await ctx.send(await self.bot.getGlobalMessage(ctx.personality,"api_error"))
						continue
					if faces:
						b = await self.bot.funcs.bytes_download_images(ctx,url,images)
						if b is None:
							continue
						elif b is False:
							return
						i = Image.open(b).convert("RGBA")
						for face in faces:
							l = face["faceRectangle"]
							t,l,w,h = l.values()
							d = ImageDraw.Draw(i)
							d.rectangle([(l,t),(int(l+w),int(t+h))],outline="orange")
						final = BytesIO()
						i.save(final,"png")
						final.seek(0)
						await ctx.send(file=discord.File(final,"faces.png"))
				else:
					await ctx.send(await self.bot.getGlobalMessage(ctx.personality,"no_faces"))
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@checks.is_bot_owner()
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def paste(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			image = await self.get_images(ctx,urls=None,limit=1)
			pastes = await self.get_images(ctx,urls=urls,limit=8)
			didface = False
			if not pastes or image:
				return
			if image:
				image = image[0]
				faces = await self.face.detect(image,landmarks=False)
				if "error" in faces:
					await ctx.send(await self.bot.getGlobalMessage(ctx.personality,"api_error"))
					return
				if faces:
					b = await self.funcs.bytes_download(image)
					if b is None:
						return
					elif b is False:
						return
					main = Image.open(b).convert("RGBA")
					for i,url in enumerate(pastes):
						if i > len(faces)-1:
							break
						if not faces[i] is None:
							b2 = await self.funcs.bytes_download(url)
							face = faces[i]
							i = Image.open(b2).convert("RGBA")
							l = face["faceRectangle"]
							t,l,w,h = l.values()
							i = i.resize((w,h))
							main.paste(i,(l,t),i)
							didface = True
					final = BytesIO()
					main.save(final,"png")
					final.seek(0)
					if didface:
						await ctx.send(file=discord.File(final,"pastes.png"))
					else:
						await ctx.send(":thinking: For some reason no pastes were made.")
				else:
					await ctx.send(await self.bot.getGlobalMessage(ctx.personality,"no_faces"))
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)
			traceback.print_exc()

def setup(bot):
	bot.add_cog(Face(bot))
