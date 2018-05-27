from discord.ext import commands
import discord
from random import *
import urllib
import xml.etree.ElementTree as ET
from utils import checks
import asyncio
import aiohttp
#from aiosocksy.connector import ProxyConnector, ProxyClientRequest
import json
from urllib.parse import urlparse
import traceback
from bs4 import BeautifulSoup
import re

class NSFW():

	def __init__(self,bot):
		self.bot = bot
		self.funcs = self.bot.funcs
		self.cursor = self.bot.mysql.cursor
		self.sure = "bmF1Z2h0eWJvaQ=="
		self.faOptRegex = re.compile("--(\w*) ([\d\w]*)")
		self.faUrlIDRegex = re.compile("\/(\d*[^/])\/")

	async def check(self,ctx):
		if isinstance(ctx.channel, discord.TextChannel):
			val = await self.funcs.getServerOption(ctx.guild.id,"nsfw_enabled")
			if val == "true":
				return True
			elif val == "false":
				await ctx.send(await self.funcs.getGlobalMessage(ctx.personality,"nsfw_disabled"))
				return False
			elif val is None:
				return True
			else:
				await ctx.send(await self.funcs.getGlobalMessage(ctx.personality,"nsfw_disabled"))
				return False
		else:
			return True

	async def FAPost(self,**kwargs):
		try:
			headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}
			url = kwargs.pop("url",None)
			id = kwargs.pop("id",None)
			full = kwargs.pop("full",False)
			if not url and not id:
				return []
			if not id and url:
				id = re.search(self.faUrlIDRegex,url)
				if id:
					id = id.group(0).replace("/","")
			url = "http://www.furaffinity.net/" + ("full" if full else "view") + "/" + id + "/"
			response = await self.funcs.http_get(url,headers=headers)
			data = BeautifulSoup(response,"html.parser")
			postdata = {}
			postdata["dtype"] = "post"
			postdata["by"] = data.find("td",attrs={"class":"cat","valign":"middle","align":"left"}).find("a").text
			postdata["name"] =  data.find("img",attrs={"id":"submissionImg"}).get("alt")
			postdata["url"] = url
			postdata["rating"] = data.find("td",attrs={"valign":"top","align":"left","class":"alt1 stats-container"}).find("img").get("alt").split(" ")[0].lower()
			postdata["image"] = "http:" + data.find("img",attrs={"id":"submissionImg"}).get("src")
			preview = "http:"+data.find("img",attrs={"id":"submissionImg"}).get("data-preview-src")
			postdata["previews"] = {"200":re.sub(r"[@]\d\d\d","@200",preview),"400":re.sub(r"[@]\d\d\d","@400",preview),"800":re.sub(r"[@]\d\d\d","@800",preview)}
			postdata["id"] = id
			return postdata
		except Exception as e:
			print(e)
			return None

	async def FAPopular(self,**kwargs):
		try:
			type = kwargs.pop("type",["art"])
			headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}
			response = await self.bot.funcs.http_get("http://www.furaffinity.net",headers=headers)
			results = []
			data = BeautifulSoup(response,"html.parser")
			posts_art = data.find("section",attrs={"id":"gallery-frontpage-submissions"})
			posts_writing = data.find("section",attrs={"id":"gallery-frontpage-writing"})
			posts_music = data.find("section",attrs={"id":"gallery-frontpage-music"})
			posts_crafts = data.find("section",attrs={"id":"gallery-frontpage-crafts"})
			types = {"art":posts_art,"writing":posts_writing,"music":posts_music,"crafts":posts_crafts}
			doTypes = []
			for t in type:
				doTypes.append(types[t])
			for type in doTypes:
				posts = type.find_all('figure')
				for post in posts:
					postdata = {}
					fig = post.find("figcaption")
					text = fig.find_all("a")
					postdata["dtype"] = "search_result"
					postdata["name"] = text[0].text
					postdata["by"] = text[1].text
					postdata["rating"] = post["class"][0].replace("r-","")
					postdata["type"] = post["class"][1].replace("t-","")
					postdata["url"] = "http://www.furaffinity.net" + text[0].get("href")
					preview = "http:"+post.find("img").get("src")
					postdata["previews"] = {"200":re.sub(r"[@]\d\d\d","@200",preview),"400":re.sub(r"[@]\d\d\d","@400",preview),"800":re.sub(r"[@]\d\d\d","@800",preview)}
					postdata["id"] = (post.get("id")).replace("sid-","")
					results.append(postdata)
			return results
		except Exception as e:
			return None

	async def FASearch(self,**kwargs):
		try:
			query = kwargs.pop("query","")
			results = kwargs.pop("results",48)
			range = kwargs.pop("range","all")
			page = kwargs.pop("page",1)
			order = kwargs.pop("order","relevancy")
			direction = kwargs.pop("direction","desc")
			rating = kwargs.pop("rating",["general"])
			type = kwargs.pop("type",["art"])
			id = kwargs.pop("id",None)
			headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}
			if id:
				results = await self.FAPost(id=id)
				return results
			data = {
				"q": query,
				"page": page,
				"perpage": results,
				"order-by": order,
				"order-direction": direction,
				"range": range,
				"mode": "extended"
			}
			if page is 1:
				del data["page"]
			types = ["art","music","flash","photo","story","poetry"]
			for i in rating:
				data["rating-"+i] = "on"
			for i in types:
				if i in type:
					data["type-"+i] = "on"
			response = await self.bot.funcs.http_post("http://www.furaffinity.net/search",headers=headers,params=data)
			data = BeautifulSoup(response,"html.parser")
			results = []
			posts = data.find_all('figure')
			for post in posts:
				postdata = {}
				fig = post.find("figcaption")
				text = fig.find_all("a")
				postdata["type"] = "search_result"
				postdata["name"] = text[0].text
				postdata["by"] = text[1].text
				postdata["rating"] = post["class"][0].replace("r-","")
				postdata["type"] = post["class"][1].replace("t-","")
				postdata["url"] = "http://www.furaffinity.net" + text[0].get("href")
				preview = "http:"+post.find("img").get("src")
				postdata["previews"] = {"200":re.sub(r"[@]\d\d\d","@200",preview),"400":re.sub(r"[@]\d\d\d","@400",preview),"800":re.sub(r"[@]\d\d\d","@800",preview)}
				postdata["id"] = (post.get("id")).replace("sid-","")
				results.append(postdata)
			return results
		except Exception as e:
			print(e)
			return None



	async def getDeviantArt(self,**kwargs):
		query = kwargs.pop("query")
		furry = kwargs.pop("furry",False)

		ctx = kwargs.pop("ctx",None)
		no_no = False
		no = (await self.bot.funcs.b64decode(self.sure))
		if query.startswith(no) or query == no:
			no_no = True
			if query == no:
				query = ""
			else:
				query = query.replace(await self.bot.funcs.b64decode(self.sure)+" ","",1)
			if ctx:
				if isinstance(ctx.message.channel, discord.TextChannel):
					await ctx.message.delete()
		if furry:
			query = "tag:anthro " + query
		offset = kwargs.pop("offset", randint(0,700))
		url = "https://backend.deviantart.com/rss.xml?type=deviation&offset={0}&q={1}".format(offset,urllib.parse.quote_plus(query))
		response = await self.bot.funcs.http_get(url=url)
		if not response:
			return
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
			max_attempts = 6
			offset-=60
			for i in range(max_attempts):
				offset+=60
				url = "https://backend.deviantart.com/rss.xml?type=deviation&offset={0}&q={1}".format(offset,urllib.parse.quote_plus(query))
				response = await self.bot.funcs.http_get(url=url)
				if response:
					items = ET.fromstring(response).findall("channel/item")
					for post in items:
						if post.find("{http://search.yahoo.com/mrss/}rating").text == "adult":
							try:
								mediaurl = post.find("{http://search.yahoo.com/mrss/}content")
								mediaurl = mediaurl.get("url")
								source = post.find("link").text
								no_nos.append({"url": mediaurl, "source": source})
							except:
								continue
			if len(no_nos) > 1:
				return no_nos[randint(0,len(no_nos)-1)]
		for i in range(10):
			try:
				random = randint(0,len(items)-1)
				item = items[random]
				mediaurl = item.find("{http://search.yahoo.com/mrss/}content")
				mediaurl = mediaurl.get("url")
				rating = item.find("{http://search.yahoo.com/mrss/}rating")
				link = item.find("link")
				link = link.text
				if item.find("{http://search.yahoo.com/mrss/}content").get("medium") == "image":
					#mediaurl = media.get("url")
					return {"url": mediaurl, "source": link}
			except Exception as e:
				continue
		return False

	@commands.command(aliases=["da"])
	@checks.nsfw()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def deviantart(self,ctx,*,query:str=""):
		if not await self.check(ctx):
			return False
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

	@commands.command(hidden=True)
	@checks.nsfw()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def yiff(self,ctx,*,query:str=None):
		if not await self.check(ctx):
			return False
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			before=None
			if randint(0,1) == 1:
				before=str(randint(1,90)) + "d"
			response = (await self.bot.funcs.getReddit("yiff",nsfw=True,video=False,before=before,query=query if query else ""))
			if response:
				response = response["data"]
			for i in range(10):
				ind = randint(0,len(response)-1)
				post = response[ind]
				url = None
				if "url" in post:
					domain = urlparse(post["url"]).netloc
					if domain == "imgur.com":
							purl = await self.funcs.imgurToImageUrl(post["url"])
							if purl:
								url = {"url":purl,"source":post["full_link"]}
								break
				if "preview" in post:
					url = {"url":post["preview"]["images"][0]["source"]["url"],"source":post["full_link"]}
					break

			if url is None:
				await wait.edit(content=(await self.bot.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result")))
				return
			embed = discord.Embed(title=":camera: **Source**",type="rich",color=discord.Color.purple(),url=url["source"])
			embed.set_image(url=url["url"])
			await wait.delete()
			await ctx.send(embed=embed)

		except Exception as e:
			await ctx.send("`{0}`".format(e))
			traceback.print_exc()

	@commands.command(aliases=["fabomb"])
	@checks.is_special()
	@checks.nsfw()
	@commands.cooldown(1,10,commands.BucketType.guild)
	async def furaffinitybomb(self,ctx,*,query:str=""):
		if not await self.check(ctx):
			return False
		try:
			reArgs = re.findall(self.faOptRegex,query)
			validOpts = ("page","results","range","order","direction","type")
			override = False
			forceopts = {}
			if reArgs:
				try:
					query = (re.sub(self.faOptRegex,"",query)).rstrip()
					for i,arg in enumerate(reArgs):
						argName = arg[0]
						if not argName.lower() in validOpts:
							continue
						argValue = None
						if arg[1]:
							argValue = arg[1]
						forceopts[argName] = argValue
					override=True
				except Exception as e:
					print(e)
					pass
			order = "desc" if not randint(0,5) is 4 else "asc"
			sort = "relevancy" if not randint(0,5) is 4 else "popularity"
			page = randint(1,10)
			pop = False
			if override:
				results = await self.FASearch(query=query,**forceopts)
				if not results:
					await ctx.send(await self.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result"))
					return False
			else:
				if query == "":
					results = await self.FAPopular()
					pop = True
				else:
					results = await self.FASearch(query=query,order=sort,direction=order,page=page)
				if results is None:
					await ctx.send(await self.funcs.getCommandMessage(ctx.personality,ctx,"error"))
				if not results and pop is False:
					results = await self.FASearch(query=query,order=sort,direction=order,page=1)
				if not results:
					await ctx.send(await self.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result"))
					return False
			for post in results[:3]:
				source = post["url"]
				pic = post["previews"]["800"]
				embed = discord.Embed(title=":camera: **Source**",type="rich",color=discord.Color.purple(),url=source)
				embed.set_image(url=pic)
				await ctx.send(embed=embed)
				await asyncio.sleep(0.25)
		except Exception as e:
			traceback.print_exc()
			await ctx.send("`{0}`".format(e))

	@commands.command(aliases=["fa"])
	@checks.is_special()
	@checks.nsfw()
	@commands.cooldown(1,5,commands.BucketType.guild)
	async def furaffinity(self,ctx,*,query:str=""):
		if not await self.check(ctx):
			return False
		try:
			reArgs = re.findall(self.faOptRegex,query)
			validOpts = ("page","results","range","order","direction","type","id")
			override = False
			forceopts = {}
			if reArgs:
				try:
					query = (re.sub(self.faOptRegex,"",query)).rstrip()
					for i,arg in enumerate(reArgs):
						argName = arg[0]
						if not argName.lower() in validOpts:
							continue
						argValue = None
						if arg[1]:
							argValue = arg[1]
						forceopts[argName] = argValue
					override=True
				except Exception as e:
					print(e)
					pass
			order = "desc" if not randint(0,5) is 4 else "asc"
			sort = "relevancy" if not randint(0,5) is 4 else "popularity"
			page = randint(1,10)
			pop = False
			if override:
				results = await self.FASearch(query=query,**forceopts)

				if not results:
					await ctx.send(await self.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result"))
					return False
			else:
				if query == "":
					results = await self.FAPopular()
					pop = True
				else:
					results = await self.FASearch(query=query,order=sort,direction=order,page=page)
				if results is None:
					await ctx.send(await self.funcs.getCommandMessage(ctx.personality,ctx,"error"))
				if not results and pop is False:
					results = await self.FASearch(query=query,order=sort,direction=order,page=1)
				if not results:
					await ctx.send(await self.funcs.getGlobalMessage(ctx.personality,"nsfw_no_search_result"))
					return False
			if "id" in forceopts:
				pic = results["image"]
				source = results["url"]
			else:
				post = results[randint(0,len(results)-1)]
				pic = post["previews"]["800"]
				source = post["url"]
			embed = discord.Embed(title=":camera: **Source**",type="rich",color=discord.Color.purple(),url=source)
			embed.set_image(url=pic)
			await ctx.send(embed=embed)
		except Exception as e:
			traceback.print_exc()
			await ctx.send("`{0}`".format(e))

	@commands.command(aliases=["fur"])
	@checks.nsfw()
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def furry(self,ctx,*,query:str=""):
		if not await self.check(ctx):
			return False
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
	async def catgirl(self,ctx,txt:str=""):
		if not await self.check(ctx):
			return False
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		no_no = False
		if self.sure == (await self.bot.funcs.b64encode(txt)):
			no_no = True
			if isinstance(ctx.message.channel, discord.TextChannel):
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
