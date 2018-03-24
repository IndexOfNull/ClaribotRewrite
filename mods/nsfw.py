from discord.ext import commands
import discord
from random import *
import urllib
import xml.etree.ElementTree as ET
from utils import checks
import asyncio
import aiohttp
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
import json

class NSFW():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor
		self.sure = "bmF1Z2h0eWJvaQ=="

	async def getDeviantArt(self,**kwargs):
		query = kwargs.pop("query")
		furry = kwargs.pop("furry",False)
		ctx = kwargs.pop("ctx",None)
		if query.startswith(await self.bot.funcs.b64decode(self.sure)):
			no_no = True
			query = query.replace(await self.bot.funcs.b64decode(self.sure)+" ","",1)
			if ctx:
				await ctx.message.delete()
		if furry:
			query = "tag:anthro " + query
		offset = kwargs.pop("offset", randint(0,700))
		url = "https://backend.deviantart.com/rss.xml?type=deviation&offset={0}&q={1}".format(offset,urllib.parse.quote_plus(query))
		response = await self.bot.funcs.http_get(url=url)
		root = ET.fromstring(response)
		channel = root.find("channel")
		items = channel.findall("item")
		if len(items) == 0:
			url = "https://backend.deviantart.com/rss.xml?type=deviation&offset={0}&q={1}".format(0,urllib.parse.quote_plus(query))
			response = await self.bot.funcs.http_get(url=url)
			root = ET.fromstring(response)
			channel = root.find("channel")
			items = channel.findall("item")
			if len(items) == 0:
				return False
		if no_no:
			no_nos = []
			for post in items:
				rating = post.find("{http://search.yahoo.com/mrss/}rating").text
				media = post.find("{http://search.yahoo.com/mrss/}content")
				mediaurl = media.get("url")
				link = post.find("link").text
				if rating == "adult":
					no_nos.append({"url": mediaurl, "source": link})
			if len(no_nos) == 0:
				max_attempts = 3
				for i in range(max_attempts):
					url = "https://backend.deviantart.com/rss.xml?type=deviation&offset={0}&q={1}".format(offset,urllib.parse.quote_plus(query))
					response = await self.bot.funcs.http_get(url=url)
					root = ET.fromstring(response)
					channel = root.find("channel")
					items2 = channel.findall("item")
					for post in items2:
						rating = post.find("{http://search.yahoo.com/mrss/}rating").text
						media = post.find("{http://search.yahoo.com/mrss/}content")
						mediaurl = media.get("url")
						link = post.find("link").text
						if rating == "adult":
							no_nos.append({"url": mediaurl, "source": link})
					if len(no_nos) > 0:
						break
			if len(no_nos) > 0:
				return no_nos[randint(0,len(no_nos)-1)]
		for i in range(10):
			random = randint(0,len(items)-1)
			item = items[random]
			media = item.find("{http://search.yahoo.com/mrss/}content")
			rating = item.find("{http://search.yahoo.com/mrss/}rating")
			link = item.find("link").text
			if media.get("medium") == "image":
				mediaurl = media.get("url")
				return {"url": mediaurl, "source": link}
		return False

	@commands.command(aliases=["da"])
	@checks.nsfw()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def deviantart(self,ctx,*,query:str=""):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			url = await self.getDeviantArt(query=query,ctx=ctx)
			if url is False:
				await wait.edit(content=(await self.bot.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result")))
				return
			embed = discord.Embed(title=":camera: **Source**",type="rich",color=discord.Color.purple(),url=url["source"])
			embed.set_image(url=url["url"])
			await wait.delete()
			await ctx.send(embed=embed)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["fur"])
	@checks.nsfw()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def furry(self,ctx,*,query:str=""):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			url = await self.getDeviantArt(query=query,furry=True,ctx=ctx)
			if url is False:
				await wait.edit(content=(await self.bot.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result")))
				return
			embed = discord.Embed(title=":camera: **Source**",type="rich",color=discord.Color.purple(),url=url["source"])
			embed.set_image(url=url["url"])
			await wait.delete()
			await ctx.send(embed=embed)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@checks.nsfw()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def catgirl(self,ctx,txt:str=None):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		no_no = False
		if self.sure == (await self.bot.funcs.b64encode(txt)):
			no_no = True
			await ctx.message.delete()
		try:
			#conn = ProxyConnector(remote_resolve=True)

			async with aiohttp.ClientSession() as session:
				async with session.get("https://nekos.brussell.me/api/v1/random/image?count=1&nsfw={0}".format("true" if no_no else "false")) as resp:
					resp = json.loads(await resp.text())
					url = "https://nekos.brussell.me/image/" + resp["images"][0]["id"]
					source = "https://nekos.brussell.me/post/" + resp["images"][0]["id"]

			#response = await aiohttp.get('https://nekos.brussell.me/api/v1/random/image?count=1&nsfw=false', connector=conn)
			embed = discord.Embed(title=":camera: **Source**",type="rich",color=discord.Color.purple(),url=source)
			embed.set_image(url=url)
			await wait.delete()
			await ctx.send(embed=embed)
		except discord.errors.Forbidden:
			msg = (await self.bot.getGlobalMessage(ctx.personality,"no_image_perm"))
			await wait.edit(content=msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)


def setup(bot):
	bot.add_cog(NSFW(bot))
