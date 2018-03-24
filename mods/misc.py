import discord
from discord.ext import commands
from random import *
import hashlib

class Misc():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor
		self.getGlobalMessage = self.bot.funcs.getGlobalMessage
		self.getCommandMessage = self.bot.funcs.getCommandMessage

	@commands.command()
	@commands.cooldown(1,2,commands.BucketType.user)
	async def reverse(self,ctx,*,txt:str):
		await ctx.send(txt[::-1])

	@commands.command()
	@commands.cooldown(1,2,commands.BucketType.user)
	async def upsidedown(self,ctx,*,txt:str):
		rot180={
			' ' : ' ',
    		'a' : '\u0250', # ɐ
    		'b' : 'q',
    		'c' : '\u0254', # ɔ
    		'd' : 'p',
    		'e' : '\u0258', # ǝ
    		'f' : '\u025F', # ɟ
    		'g' : '\u0183', # ƃ
    		'h' : '\u0265', # ɥ
    		'i' : '\u0131', # ı
    		'j' : '\u027E', # ɾ
    		'k' : '\u029E', # ʞ
    		'l' : '\u0285', # ʅ
    		'm' : '\u026F', # ɯ
    		'n' : 'u', # u
			'o' : 'o',
    		'p' : 'd',
			'q': 'p',
    		'r' : '\u0279', # ɹ
			's' : 's',
    		't' : '\u0287', # ʇ
    		'u' : 'n',
    		'v' : '\u028C', # ʌ
    		'w' : '\u028D', # ʍ
			'x' : 'x',
    		'y' : '\u028E', # ʎ
			'z' : 'z',
    		'.' : '\u02D9', # ˙
    		'[' : ']',
    		'(' : ')',
    		'{' : '}',
    		'?' : '\u00BF', # ¿
    		'!' : '\u00A1', # ¡
    		"\'" : ',',
    		'<' : '>',
    		'_' : '\u203E', # ‾
    		'"' : '\u201E', # „
    		'\\' : '\\',
    		';' : '\u061B', # ؛
    		'\u203F' : '\u2040', # ‿ --> ⁀
    		'\u2045' : '\u2046', # ⁅ --> ⁆
    		'\u2234' : '\u2235', # ∴ --> ∵
    }
		final = ""
		for char in txt.lower():
			if char not in rot180:
				continue
			final += rot180[char]
		await ctx.send(final)


	@commands.command(aliases=["randomnumber"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def random(self,ctx,min:int=1,max:int=10):
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		if min > max:
			msg = (await self.bot.getCommandMessage(ctx.personality,ctx,"min-greater","random-number"))
			await wait.delete()
			await ctx.send(msg)
		try:
			await ctx.trigger_typing()
			num = randint(min,max)
			embed = discord.Embed(title="Random Number",type="rich",color=discord.Color.purple())
			embed.add_field(name="Min",value=str(min),inline=True)
			embed.add_field(name="Max",value=str(max),inline=True)
			embed.add_field(name="Number",value=str(num),inline=False)
			await ctx.send(embed=embed)
			await wait.delete()
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["randomcolor"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def color(self,ctx):
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			r,g,b = (randint(0,255),randint(0,255),randint(0,255))
			hexcode = '#%02x%02x%02x' % (r, g, b)
			embed = discord.Embed(title="Random Color",type="rich",color=discord.Color.from_rgb(r,g,b))
			embed.add_field(name="Hex",value=hexcode,inline=False)
			embed.add_field(name="RGB",value="{0},{1},{2}".format(r,g,b),inline=False)
			await ctx.send(embed=embed)
			await wait.delete()
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["cryptocurrency"])
	@commands.cooldown(1,3,commands.BucketType.guild)
	async def crypto(self,ctx,incur:str,to:str):
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			url = "https://min-api.cryptocompare.com/data/price?fsym=" + incur.upper() + "&tsyms=" + to.upper()
			resp = await self.bot.funcs.http_get_json(url)
			if resp is False:
				msg = (await self.getGlobalMessage(ctx.personality,"api_error"))
				await wait.edit(content=msg)
				return
			if "Response" in resp:
				msg = (await self.getCommandMessage(ctx.personality,ctx,"invalid-codes"))
				await wait.edit(content=msg)
				return
			if to.upper() in resp:
				msg = "1 " + incur.upper() + " :arrow_right: " + str(resp[to.upper()]) + " " + to.upper() + " (according to CryptoCompare.com)"
				await wait.edit(content=msg)
			else:
				msg = (await self.getCommandMessage(ctx.personality,ctx,"invalid-codes"))
				await wait.edit(msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["coin"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def flip(self,ctx):
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			faces = ["Heads","Tails"]
			face = faces[randint(0,1)]
			await wait.edit(content=(await self.getCommandMessage(ctx.personality,ctx,"message")).format(face))
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command(aliases=["dice"])
	@commands.cooldown(1,2,commands.BucketType.user)
	async def roll(self,ctx,count:int=2,sides:int=6):
		if count > 20:
			await ctx.send((await self.getCommandMessage(ctx.personality,ctx,"high_count")).format(20))
			return
		elif sides > 50:
			await ctx.send((await self.getCommandMessage(ctx.personality,ctx,"high_sides")).format(50))
			return
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			rolls = []
			for i in range(count):
				rolls.append(str(randint(1,sides)))
			rolls = ", ".join(rolls)
			embed = discord.Embed(title="Dice Roll",type="embed",color=discord.Color.green())
			embed.add_field(name="Dice Count",value=str(count),inline=True)
			embed.add_field(name="Side Count",value=str(sides),inline=True)
			embed.add_field(name="Rolls",value=rolls,inline=False)
			await wait.delete()
			await ctx.send(embed=embed)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def md5(self,ctx,content:str):
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			content = content.encode("utf-8")
			hashed = hashlib.md5(content).hexdigest()
			embed = discord.Embed(title="Hashing Function",type="rich",color=discord.Color.gold())
			embed.add_field(name="Algorithm",value="MD5",inline=False)
			embed.add_field(name="Hash",value=hashed,inline=False)
			await wait.delete()
			await ctx.send(embed=embed)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def sha256(self,ctx,content:str):
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			content = content.encode("utf-8")
			hashed = str(hashlib.sha256(content).hexdigest())
			embed = discord.Embed(title="Hashing Function",type="rich",color=discord.Color.gold())
			embed.add_field(name="Algorithm",value="MD5",inline=False)
			embed.add_field(name="Hash",value=hashed,inline=False)
			await wait.delete()
			await ctx.send(embed=embed)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.user)
	async def avatar(self,ctx,user:discord.User=None):
		if user is None:
			user = ctx.message.author
		wait = await ctx.send((await self.bot.funcs.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			embed = discord.Embed(title="User Avatar",type="rich",color=discord.Color.teal(),description="{0.name}#{0.discriminator}".format(user))
			#embed.add_field(name="User",value="{0.name}#{0.discriminator}".format(user),inline=False)
			embed.set_image(url=user.avatar_url)
			await wait.delete()
			await ctx.send(embed=embed)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)


def setup(bot):
	bot.add_cog(Misc(bot))
