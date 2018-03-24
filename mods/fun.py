from discord.ext import commands
import discord
from PIL import Image
from PIL import ImageFont
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFilter
from io import BytesIO, StringIO
import textwrap
import sys, os
from random import *
import urllib

class Fun():
	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor
		self.get_images = self.bot.get_images

	#Image Based Commands

	@commands.command(hidden=True)
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def whatdidyousayaboutevan(self,ctx):
		try:
			await ctx.send(file=discord.File("resource/img/evano.png"))
			await ctx.send("WHAT DID YOU SAY ABOUT EVAN!")
		except Exception as e:
			print("oh no, evan died")

	@commands.command(aliases=["loganpaul"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def logan(self,ctx, *url):
		if not url:
			url = None
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						print("One image failed to download")
						continue
					elif b is False:
						print("The one and only failed")
						return
					img = Image.open(b).convert("RGBA")
					w, h = img.size
					logan = Image.open("resource/img/loganpaul.png").convert("RGBA")
					wresize, hresize = int(w/1.5), int(h/1.25)
					logan.thumbnail((wresize, hresize))

					rw, rh = logan.size
					img.paste(logan, (w-rw,h-rh), logan)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"logan.png")
					await ctx.send(file=upload)
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)
			#ignored, notification of error will be handled by bot.py

	@commands.command(aliases=["trophy"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def participation(self,ctx,user:discord.User=None):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			if user is None:
				user = ctx.message.author

			await ctx.trigger_typing()
			trophy = Image.open("resource/img/trophy.png").convert("RGBA")
			text = "Thanks for participating,\n " + user.display_name
			offset = [315,720]
			font = ImageFont.truetype("resource/font/GenBasR.ttf",28)
			d = ImageDraw.Draw(trophy)
			for line in textwrap.wrap(text,width=25):
				d.text(offset,line,font=font,fill="#000")
				offset[1] += font.getsize(line)[1]
			final = BytesIO()
			trophy.save(final,"png")
			final.seek(0)
			upload = discord.File(final,"trophy.png")
			await ctx.send(file=upload)
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["grumistake"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def gru(self,ctx,user:discord.User=None):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			if user is None:
				user = ctx.message.author
			await ctx.trigger_typing()
			img = Image.open((await self.bot.funcs.bytes_download(user.avatar_url)))
			imgr = img.resize((244,244))
			gru = Image.open("resource/img/grumistake.png").convert("RGBA")
			gru.paste(imgr, (452,685))
			gru.paste(imgr, (1200,688))
			final = BytesIO()
			gru.save(final,"png")
			final.seek(0)
			upload = discord.File(final,"GRUUUU.png")
			await wait.delete()
			await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def notarobot(self, ctx, *url):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					w,h = img.size
					nar = Image.open("resource/img/notarobot.png").convert("RGBA")
					rwidth = int(w/1.2)
					rheight = int(h/1.2)
					nar.thumbnail((rwidth,rheight))
					narw, narh = nar.size
					img.paste(nar, (w-narw,h-narh), nar)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"notarobot.png")
					await ctx.send(file=upload)
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["guyfieri"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def fieri(self,ctx,*url):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					w,h = img.size
					guy = Image.open("resource/img/feelmyfieri.png").convert("RGBA")
					rwidth = int(w/2)
					rheight = int(h/1.3)
					guy.thumbnail((rwidth,rheight))
					guyw, guyh = guy.size
					img.paste(guy, (w-guyw,h-guyh), guy)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"feelmyfieri.png")
					await ctx.send(file=upload)
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def bandicam(self,ctx,*url):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					w,h = img.size
					bc = Image.open("resource/img/bandicam.png").convert("RGBA")
					rwidth = int(w/2)
					rheight = int(h/1.2)
					bc.thumbnail((rwidth,rheight))
					bcw, bch = bc.size
					center = int(w/2 - bcw/2)
					img.paste(bc, (center,0), bc)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"bandicam.png")
					await ctx.send(file=upload)
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["cmm"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def changemymind(self,ctx,*,text:str):
		if len(text) > 65:
			return
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			image = Image.open("resource/img/changemymind.png").convert("RGBA")
			offset = [0,0]
			font = ImageFont.truetype("resource/font/OpenSans-Semibold.ttf",28)
			txt=Image.new('RGBA', (265,100))
			d = ImageDraw.Draw(txt)
			"""for line in textwrap.wrap(text,width=25):
				d.text(offset,line,font=font,fill="#000")
				offset[1] += font.getsize(line)[1]"""
			width,height= d.textsize(text, font=font)
			linelen = 18
			ntext = "\n".join([text[i:i+linelen] for i in range(0, len(text), linelen)])
			d.multiline_text((0,0),ntext,fill="#000",font=font,align="center")
			txt = txt.transform(txt.size, Image.PERSPECTIVE, (1, 0, 0, 0, 1, 0, -0.0003, 0))
			txt = txt.rotate(22, expand=1)
			mlwidth, mlheight = d.multiline_textsize(ntext, font=font)
			xoffset = int(mlheight*0.42045454545455)
			print(height)
			image.paste(txt, (393-xoffset,265-mlheight), txt)
			final = BytesIO()
			image.save(final,"png")
			final.seek(0)
			upload = discord.File(final,"changemymind.png")
			await wait.delete()
			await ctx.send(file=upload)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["whatis"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def identify(self, ctx, *url):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=2)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					data = {
						"Content": url,
						"Type": "CaptionRequest",
					}
					headers = {
						"Content-Type": "application/json; charset=utf-8"
					}
					resp = await self.bot.funcs.http_post("https://captionbot.azurewebsites.net/api/messages",params=data,headers=headers,json=True)
					await wait.edit(content=resp)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["newfunky","funkymode","newfunkymode"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def funky(self, ctx, *url):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		channel = ctx.message.channel
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			print(images)
			if images:
				for url in images:
					print("GOOD")
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)

					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					w,h = img.size
					nfm = Image.open("resource/img/newfunkymode.png").convert("RGBA")
					rwidth = int(w/1.2)
					rheight = int(h/1.4)
					nfm.thumbnail((rwidth,rheight))
					nfmw, nfmh = nfm.size
					img.paste(nfm, (w-nfmw,0), nfm)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"newfunkymode.png")
					await channel.send(file=upload)
					final = None
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["sonic3","knuckles"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def andknuckles(self, ctx, *url):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			images = await self.get_images(ctx, urls=url, limit=3)
			if images:
				for url in images:
					b = await self.bot.funcs.bytes_download_images(ctx,url,images)
					if b is None:
						continue
					if b is False:
						return
					img = Image.open(b).convert("RGBA")
					w,h = img.size
					an = Image.open("resource/img/andknuckles.png").convert("RGBA")
					rwidth = int(w/1.6)
					rheight = int(h/1.8)
					an.thumbnail((rwidth,rheight))
					anw, anh = an.size
					img.paste(an, (int((w-anw)-anw*0.05),int((h-anh)-anh*0.05)), an)
					final = BytesIO()
					img.save(final,"png")
					final.seek(0)
					if sys.getsizeof(final) > 8388608:
						msg = (await self.bot.getGlobalMessage(ctx.personality,"final_upload_too_big"))
						await ctx.send(msg)
						continue
					upload = discord.File(final,"andknuckles.png")
					await ctx.send(file=upload)
			await wait.delete()
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)


	#Text Based Commands

	@commands.command(aliases=["roast"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def insult(self, ctx, user:discord.User=None):
		#wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			if user is None:
				user = ctx.message.author
			templates = [
			"You are <adjective>",
			"You look like <article target=id> <adjective id=id> <animal>",
			"Everyone thinks you are <animal> <animal_part>",
			"	You are as <adjective> as <article target=adj1> <adjective min=1 max=3 id=adj1> <amount> of <adjective min=1 max=3> <animal> <animal_part>"
			]
			template = templates[randint(0,len(templates)-1)]
			params = urllib.parse.urlencode({
				'template': template
			})
			url = "https://insult.mattbas.org/api/insult.json?%s" % params
			resp = await self.bot.funcs.http_get_json(url)
			stop = False
			if resp is False: stop = True
			if resp["error"] is True: stop = True
			if stop:
				msg = (await self.bot.getGlobalMessage(ctx.personality,"api_error"))
				await ctx.send(content=msg)
				return
			await ctx.send(content="{0.mention} {1}".format(user,resp["insult"]))
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["dad"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def dadjoke(self, ctx):
		#wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			headers = {"Accept": "application/json"}
			url = "https://icanhazdadjoke.com"
			resp = await self.bot.funcs.http_get_json(url,headers=headers)
			stop = False
			if resp is False: stop = True
			if resp["status"] == 400: stop = True
			if stop:
				msg = (await self.bot.getGlobalMessage(ctx.personality,"api_error"))
				await ctx.send(content=msg)
				return
			await ctx.send(resp["joke"])
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["8ball"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def eightball(self, ctx, question:str):
		#wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			responses = [
			"It is certain",
			"It is decidedly so",
			"Without a doubt",
			"Yes, definitely",
			"You may rely on it",
			"As I see it, yes",
			"Most likely",
			"Outlook good",
			"Yes",
			"Signs point to yes",
			"Reply hazy, try again",
			"Ask again later",
			"Better not tell you now",
			"Cannot predict now",
			"Concentrate and ask again",
			"Don't count on it",
			"My reply is no",
			"My sources say no",
			"Outlook not so good",
			"Very doubtful",
			"The answer lies within",
			"That's a question for your parents",
			"Do you think I'm some kind of psychic?",
			"ERROR: Stupid Question Asked"
			]
			response = responses[randint(0,len(responses)-1)]
			await ctx.send(ctx.message.author.mention + " " + response)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,2,commands.BucketType.user)
	async def freesmiley(self,ctx):
		url = "http://bilder-lustige-bilder.de/images/{0}_lustige_smiley_bilder.jpg".format(randint(1,20))
		try:
			await ctx.trigger_typing()
			embed = discord.Embed(title=":camera: **Source**",type="rich",url="http://free-smiley.de",color=discord.Color.gold())
			embed.set_image(url=url)
			await ctx.send(embed=embed)
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)

def setup(bot):
	bot.add_cog(Fun(bot))
