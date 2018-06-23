import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageOps, ImageDraw, ImageFilter, ImageEnhance
from io import BytesIO, StringIO
import sys,os
import traceback
from random import *

class ImgManip():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.get_images = self.funcs.get_images

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def solarize(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGB")
					img = ImageOps.solarize(img,threshold=randint(1,127))
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def flip(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = ImageOps.flip(img)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def mirror(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = ImageOps.mirror(img)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def grayscale(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGB")
					img = ImageOps.grayscale(img)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)
			traceback.print_exc()

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def posterize(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGB")
					img = ImageOps.posterize(img,1)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)
			traceback.print_exc()

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def blur(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = ImageEnhance.Sharpness(img).enhance(0)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)
			traceback.print_exc()

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def sharpen(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = ImageEnhance.Sharpness(img).enhance(2)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def invert(self,ctx,*urls):
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx,urls=urls,limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGB")
					img = ImageOps.invert(img)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(img) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					await ctx.send(file=discord.File(final,"inverted.png"))
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,4,commands.BucketType.guild)
	async def rotate(self,ctx,*url):
		if not url:
			url = None
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					elif b is False:
						return
					img = Image.open(b).convert("RGBA")
					img = img.rotate(90,expand=True)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"rotated.png")
					await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await ctx.send(content=msg)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

def setup(bot):
	bot.add_cog(ImgManip(bot))
