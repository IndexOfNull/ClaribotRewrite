from pymysql.converters import escape_item, escape_string, encoders
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandNotFound, CommandError
import asyncio, aiohttp
import async_timeout
from discord.ext.commands.view import StringView
from utils import checks
from io import BytesIO
import re
import json
import datetime
import time
from dateutil import tz
from dateutil.tz import *
import base64

class Funcs():
	def __init__(self,bot,cursor):
		self.bot = bot
		self.cursor = cursor
		self.mention_regex = re.compile(r"<@!?(?P<id>\d+)>")
		self.session = aiohttp.ClientSession()
		self.image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']
		self.epoch = datetime.datetime.utcfromtimestamp(0)

	async def b64encode(self,txt):
		return base64.b64encode(txt.encode("ascii")).decode("utf-8")

	async def b64decode(self,txt):
		return base64.b64decode(txt.encode("ascii")).decode("utf-8")

	async def getUTCMillis(self,dt):
		return int((dt - self.epoch).total_seconds() * 1000.0)

	async def getUTCSeconds(self,dt):
		return int((dt - self.epoch).total_seconds())

	async def getUTCNow(self,**kwargs):
		give_dt = kwargs.pop("datetime",False)
		if give_dt:
			return datetime.datetime.utcnow()
		else:
			return (await self.getUTCSeconds(datetime.datetime.utcnow()))

	async def secondsToUTC(self,seconds):
		return datetime.datetime.utcfromtimestamp(seconds)

	async def getFormattedTime(self,dt):
		tzconverted = dt.astimezone(tz.tzlocal())
		return tzconverted.strftime("%Y-%m-%d %H:%M:%S {0}".format(tz.tzlocal().tzname(tzconverted)))

	async def getCurrentFormattedTime(self):
		current_t = datetime.datetime.now()
		tzconverted = current_t.astimezone(tz.tzlocal())
		return tzconverted.strftime("%Y-%m-%d %H:%M:%S {0}".format(tz.tzlocal().tzname(tzconverted)))

	async def confirm_command(self,ctx):
		author = ctx.message.author
		channel = ctx.message.channel
		notification = await channel.send(":pencil: I need confirmation before executing this command, please check your DMs.")
		confmsg = await author.send(":pencil: To confirm your command please send 'yes' (without quotes). You may also send 'no' (again without quotes) to cancel the request.")
		confirmed = False
		def check(message):
			nonlocal confirmed
			if message.author == author and message.content.lower() == "yes":
				confirmed=True
				return True
			elif message.author == author and message.content.lower() == "no":
				confirmed=False
				return True
		try:
			message2 = await self.bot.wait_for('message', timeout=20.0, check=check)
		except asyncio.TimeoutError:
			await notification.delete()
			await confmsg.delete()
			await author.send(':alarm_clock: Confirmation timed out')
			return False
		else:
			if confirmed:
				await author.send(':white_check_mark: The command has been confirmed.')
				await notification.delete()
				await confmsg.delete()
				return True
			elif confirmed is False:
				await author.send(':x: The command has been canceled.')
				await notification.delete()
				await confmsg.delete()
				return False
			elif confirmed is None:
				await author.send(":fire: Something went wrong")
				await notification.delete()
				await confmsg.delete()
				return False


	async def bytes_download_images(self, ctx, url, imgs):
		img = await self.bytes_download(url)
		if img is False:
			if len(imgs) == 1:
				msg = (await self.bot.funcs.getGlobalMessage(ctx.personality,"download_fail"))
				await ctx.send(msg)
				return False
			return None
		return img

	async def http_post(self, url, **kwargs):
		isjson = kwargs.pop("json",False)
		headers = kwargs.pop("headers",{})
		params = kwargs.pop("params",{})
		try:
			with async_timeout.timeout(10):
				async with self.session.post(url,headers=headers,data=json.dumps(params)) as resp:
					data = await resp.read()
					if isjson:
						data = json.loads(data)
					return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

	async def http_get(self, url, **kwargs):
		headers = kwargs.pop("headers",{})
		try:
			with async_timeout.timeout(10):
				async with self.session.get(url,headers=headers) as resp:
					data = await resp.read()
					return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

	async def http_get_json(self, url, **kwargs):
		headers = kwargs.pop("headers",{})
		try:
			with async_timeout.timeout(10):
				async with self.session.get(url,headers=headers) as resp:
					data = json.loads(await resp.text())
					return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False


	async def bytes_download(self, url:str):
		try:
			with async_timeout.timeout(10):
				async with self.session.get(url) as resp:
					data = await resp.read()
					b = BytesIO(data)
					b.seek(0)
					return b
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			return False

	async def get_tier_points(self,tier:int):
		return (684 + (684*[level-1]))-684

	async def tier_from_points(self,points:int):
		return abs(int((((points - 684)/684))+2))

	async def give_points(self,user,points:int,server,message=None):
		try:
			sql = "SELECT points FROM `points` WHERE user_id={0.id} AND server_id={1.id}".format(user,server)
			result = self.cursor.execute(sql).fetchall()

			if not result:
				final_points = points
				sql = "INSERT INTO `points` (`server_id`, `user_id`, `points`, `timestamp`) VALUES ('{3.id}', '{0.id}', '{1}', '{2}');".format(user,points,await self.getUTCNow(),server)
				result = [{"points": 0}]
			else:
				final_points = result[0]["points"] + points
				sql = "UPDATE `points` SET `points`={0}, `timestamp`={2} WHERE `user_id`={1.id} AND `server_id`={3.id}".format(final_points,user,await self.getUTCNow(),server)
			result2 = self.cursor.execute(sql)
			self.cursor.commit()
			beforeLevel = await self.tier_from_points(result[0]["points"])
			afterLevel = await self.tier_from_points(final_points)
			#print("{0}>{1}".format(afterLevel,beforeLevel))
			if afterLevel > beforeLevel:
				#print("LEVEL UP!")
				if message:
					await message.channel.send((await self.getGlobalMessage(await self.getPersonality(message.guild),"level_up")).format(user,afterLevel))
			#print("done")
			return {"before": result[0]["points"],"after": final_points}
		except Exception as e:
			print(e)
			self.cursor.rollback()
			return False

	async def get_points(self,user,guild):
		try:
			sql = "SELECT `points`, `timestamp` FROM `points` WHERE user_id={0.id} AND server_id={1.id}".format(user,guild)
			result = self.cursor.execute(sql).fetchall()
			if not result:
				return {"points": 0, "timestamp": await self.getUTCNow(), "no_row": True}
			return result[0]
		except Exception as e:
			self.cursor.rollback()
			return False

	async def set_points(self,user,points:int):
		try:
			sql = "SELECT points FROM `points` WHERE user_id={0.id}".format(user)
			result = self.cursor.execute(sql).fetchall()
			final_points = points
			if not result:
				sql = "INSERT INTO `points` (`user_id`, `points`, `timestamp`) VALUES ('{0.id}', '{1}', '{2}');".format(user,points,self.getUTCNow())
			else:
				sql = "UPDATE `points` SET points={0} WHERE user_id={1.id}".format(final_points,user)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return {"before": result[0]["points"],"after": points}
		except Exception as e:
			self.cursor.rollback()
			return False

	def find_member(self, server, name, steps=2):
		member = None
		match = self.mention_regex.search(name)
		if match:
			member = server.get_member(match.group('id'))
		if not member:
			name = name.lower()
			checks = [lambda m: m.name.lower() == name or m.display_name.lower() == name, lambda m: m.name.lower().startswith(name) or m.display_name.lower().startswith(name) or m.id == name, lambda m: name in m.display_name.lower() or name in m.name.lower()]
			for i in range(steps if steps <= len(checks) else len(checks)):
				if i == 3:
					member = discord.utils.find(checks[1], self.bot.get_all_members())
				else:
					member = discord.utils.find(checks[i], server.members)
				if member:
					break
		return member

	async def imagecheck(self, url:str, gif=False):
		try:
			with async_timeout.timeout(5):
				async with self.session.head(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type', '').lower()
						if gif:
							if mime == "image/gif":
								return True
							else:
								return False
						else:
							if any([mime == x for x in self.image_mimes]):
								return True
							else:
								return False
		except Exception as e:
			return None

	async def get_attachment_images(self, ctx, check_func, gif):

			last_attachment = None
			img_urls = []
			async for m in ctx.message.channel.history(before=ctx.message, limit=25):
				check = False

				if len(m.attachments) > 0:
					#print("getting attachments")
					last_attachment = m.attachments[0].url

					check = await check_func(last_attachment, gif)
				elif len(m.embeds) > 0:
					last_attachment = m.embeds[0].url
					check = await check_func(last_attachment, gif)
				if check:
					img_urls.append(last_attachment)
					break
			#print(last_attachment)
			return img_urls

	async def isimage(self, url:str):
		try:
			with async_timeout.timeout(5):
				async with self.session.head(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type', '').lower()
						if any([mime == x for x in self.image_mimes]):
							return True
						else:
							return False
		except Exception as e:
			return None

#Returns a list of urls if success, elsewise returns None
	async def get_images(self, ctx, **kwargs):
		try:
			personality = ctx.personality
			message = ctx.message
			channel = ctx.message.channel
			attachments = ctx.message.attachments
			mentions = ctx.message.mentions
			limit = kwargs.pop('limit', 8)
			urls = kwargs.pop('urls', [])
			gif = kwargs.pop('gif', False)
			msg = kwargs.pop('msg', True)
			if gif:
				check_func = self.isgif
			else:
				check_func = self.isimage
			if urls is None:
				urls = []
			elif type(urls) == str:
				urls = urls.split(" ")
			elif type(urls) != tuple:
				urls = [urls]
			else:
				urls = list(urls)
			scale = kwargs.pop('scale', None)
			scale_msg = None
			int_scale = None
			img_count=0
			if gif is False:
				for user in mentions:
					if user.avatar:
						#urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(user))
						urls.append('https://media.discordapp.net/avatars/{0.id}/{0.avatar}.png?size=512'.format(user))
					else:
						urls.append(user.default_avatar_url)
					img_count += 1
			for attachment in attachments:
				urls.append(attachment.url)
			if scale:
				scale_limit = scale
				img_count += 1
			if urls and len(urls) > limit:
				await channel.send((await self.getGlobalMessage(personality,"file_limit")).format(limit))
				ctx.command.reset_cooldown(ctx)
				return False
			img_urls = []
			count = 1
			for url in urls:
				user = None
				if url.startswith('<@'):
					continue
				if not url.startswith('http'):
					url = 'http://'+url
				try:
					if scale:
						s_url = url[8:] if url.startswith('https://') else url[7:]
						if str(math.floor(float(s_url))).isdigit():
							int_scale = int(math.floor(float(s_url)))
							scale_msg = '`Scale: {0}`\n'.format(int_scale)
							if int_scale > scale_limit and ctx.message.author.id != self.bot.owner.id:
								int_scale = scale_limit
								scale_msg = '`Scale: {0} (Limit: <= {1})`\n'.format(int_scale, scale_limit)
							continue
				except Exception as e:
					print(e)
					pass
				check = await check_func(url)
				if check is None:
					continue
				if check is False and gif is False:
					check = await self.isgif(url)
					if check:
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"image_command")))
						ctx.command.reset_cooldown(ctx)
						return False
					elif len(img_urls) == 0:
						name = url[8:] if url.startswith('https://') else url[7:]
						member = self.find_member(message.guild, name, 2)
						if member:
							#img_urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(member) if member.avatar else member.default_avatar_url)
							urls.append('https://media.discordapp.net/avatars/{0.id}/{0.avatar}.png?size=512'.format(user))
							count += 1
							continue
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"image_error")))
						ctx.command.reset_cooldown(ctx)
						return False
					else:
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"invalid_image")).format(count))
						continue
				elif gif and check is False:
					check = await self.isimage(url)
					if check:
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"gif_command")))
						ctx.command.reset_cooldown(ctx)
						return False
					elif len(img_urls) == 0:
						name = url[8:] if url.startswith('https://') else url[7:]
						member = self.find_member(message.guild, name, 2)
						if member:
							#img_urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(member) if member.avatar else member.default_avatar_url)
							urls.append('https://media.discordapp.net/avatars/{0.id}/{0.avatar}.png?size=512'.format(user))
							count += 1
							continue
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"image_error")))
						ctx.command.reset_cooldown(ctx)
						return False
					else:
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"invalid_image")).format(count))
						continue
				img_urls.append(url)
				count += 1
			else:
				if len(img_urls) == 0:
					attachment_images = await self.get_attachment_images(ctx, check_func)
					if attachment_images:
						img_urls.extend([*attachment_images])
					else:
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"missing_image_attachments")).format(', mention(s) ' if not gif else ' '))
						ctx.command.reset_cooldown(ctx)
						return False
			if scale:
				if len(img_urls) == 0:
					attachment_images = await self.get_attachment_images(ctx, check_func)
					if attachment_images:
						img_urls.extend([*attachment_images])
					else:
						if msg:
							await channel.send((await self.getGlobalMessage(personality,"missing_image_attachments")).format(', mention(s) ' if not gif else ' '))
						ctx.command.reset_cooldown(ctx)
						return False
				return img_urls, int_scale, scale_msg
			if img_urls:
				return img_urls
			return False
		except Exception as e:
			print(e)


	async def get_images(self,ctx,**kwargs):
		message = ctx.message
		personality = ctx.personality
		channel = message.channel
		msg = kwargs.pop("msg",True)
		urls = kwargs.pop("urls",[])
		limit = kwargs.pop("limit",3)
		gif = kwargs.pop("gif",False)
		attachments = message.attachments
		mentions = message.mentions
		if urls is None:
			urls = []
		elif type(urls) == str:
			urls = urls.split(" ")
		elif type(urls) != tuple:
			urls = [urls]
		else:
			urls = list(urls)
		img_count = len(urls) - len(mentions)
		for attachment in attachments:
			urls.append(attachment.url)
			img_count += 1
		if gif is False:
			for user in mentions:
				if user.avatar:
					#urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(user))
					urls.append('https://media.discordapp.net/avatars/{0.id}/{0.avatar}.png?size=512'.format(user))
				else:
					urls.append(user.default_avatar_url)
			img_count += 1
		if len(urls)-img_count > limit:
			if msg:
				await channel.send((await self.getGlobalMessage(personality,"file_limit")).format(limit))
			ctx.command.reset_cooldown(ctx)
			return False
		img_urls = []
		check_been_false = False
		if len(urls) == 0:
			last_image = await self.get_attachment_images(ctx,self.imagecheck,gif)
			print(last_image)
			if len(last_image) == 0:
				if msg:
					error = (await self.getGlobalMessage(personality,"missing_image_attachments")).format(', mention(s)' if not gif else ' ')
					await channel.send(error)
				ctx.command.reset_cooldown(ctx)
				return False
			img_urls.extend([*last_image])
			return img_urls
		for url in urls:
			if url.startswith("<@"):
				continue
			if not url.startswith("http"):
				url = "http://" + url
			check = await self.imagecheck(url,gif)
			if check is False:
				check_been_false = True
				print("BAD CHECK")
				if gif is True:
					if msg:
						await channel.send((await self.getGlobalMessage(personality,"gif_command")))
					ctx.command.reset_cooldown(ctx)
					continue
				elif gif is False:
					if msg:
						await channel.send((await self.getGlobalMessage(personality,"image_command")))
					ctx.command.reset_cooldown(ctx)
					continue
			if check is None:
				print("Check is none")
				continue
			img_urls.append(url)
		if len(img_urls) == 0 and not check_been_false:
			if msg:
				error = (await self.getGlobalMessage(personality,"missing_image_attachments")).format(', mention(s)' if not gif else ' ')
				await channel.send(error)
			ctx.command.reset_cooldown(ctx)
			return False
		return img_urls



	async def getPersonality(self,message):
		try:
			personality = "default"
			if isinstance(message.channel, discord.TextChannel) is True:
				sql = "SELECT personality FROM `personality` WHERE server_id={0}".format(message.guild.id)
				result = self.cursor.execute(sql).fetchall()
				if result:
					personality = result[0]["personality"]
			return personality
		except Exception as e:
			self.cursor.rollback()
			return "default"

	async def getBlacklisted(self,message):
		try:
			blacklisted = False

			if isinstance(message.channel, discord.TextChannel) is True:
				bypass = checks.is_admin(message)
				#print(bypass)
				if bypass:
					return False
				sql = "SELECT channel_id FROM `blacklist_channels` WHERE channel_id={0}".format(message.channel.id)
				result = self.cursor.execute(sql).fetchall()
				if result:
					if result[0]["channel_id"] == message.channel.id:
						blacklisted = True
				if not result:
					sql = "SELECT user_id FROM `blacklist_users` WHERE user_id={0} AND server_id={1}".format(message.author.id,message.guild.id)
					result = self.cursor.execute(sql).fetchall()
					if result:
						if result[0]["user_id"] == message.author.id:
							blacklisted = True

			return blacklisted
		except Exception as e:
			self.cursor.rollback()
			return False

	async def getGlobalMessage(self,personality,key):
		#Check to see if there will be anything wrong with getting the value, if there is have it fallback to the defaults
		if personality not in self.bot.messages:
			personality = "default"
		if "global" not in self.bot.messages[personality]:
			personality = "default"
		if key not in self.bot.messages[personality]["global"]:
			personality = "default"
		#Double check to see that the defaults are intact, you should never see one of these printed to the console
		if personality not in self.bot.messages:
			print("Something is horribly wrong with the messages.json file... (Personality not in messages.json, check to see that 'default' exists in there)")
			return False
		if "global" not in self.bot.messages[personality]:
			print("Something is horribly wrong with the messages.json file... (Global not in messages.json defaults, check to see that 'global' exists in the 'default' array)")
			return False
		if key not in self.bot.messages[personality]["global"]:
			print("Missing global personality key ({0}), check that you have it in the message defaults.".format(key))
			return False
		return self.bot.messages[personality]["global"][key]

	async def getCommandMessage(self,personality,ctx,key,cmd_name:str=None): #Hey can I copy your homework? Yeah sure just make some changes so it doesn't look suspicous
		#Check to see if there will be anything wrong with getting the value, if there is have it fallback to the defaults
		if ctx.invoked_subcommand is not None:
			name = ctx.command.name + "-" + ctx.invoked_subcommand.name
		else:
			name = ctx.command.name
		if cmd_name is not None:
			name = cmd_name
		if personality not in self.bot.messages:
			personality = "default"
		if "commands" not in self.bot.messages[personality]:
			personality = "default"
		if name not in self.bot.messages[personality]["commands"]:
			personality = "default"
		if key not in self.bot.messages[personality]["commands"][name]:
			personality = "default"
		#Double check to see that the defaults are intact, you should never see one of these printed to the console
		if personality not in self.bot.messages:
			print("Something is horribly wrong with the messages.json file... (Personality not in messages.json, check to see that 'default' exists in there)")
			return False
		if "commands" not in self.bot.messages[personality]:
			print("Something is horribly wrong with the messages.json file... ('commands' not in messages.json defaults, check to see that 'commands' exists in the 'default' array)")
			return False
		if name not in self.bot.messages[personality]["commands"]:
			print("Something is horribly wrong with the messages.json file... (Command '{0}' not in messages.json default commands, check to see that it exists)".format(message.command.name))
			return False
		if key not in self.bot.messages[personality]["commands"][name]:
			print("Missing command personality key ({0}), check to see that it is in the message defaults".format(key))
			return False
		return self.bot.messages[personality]["commands"][name][key]

	async def getPrefix(self,message):
		try:
			if self.bot.dev_mode == True:
				prefix = ","
			else:
				prefix = "$"
			if isinstance(message.channel, discord.TextChannel) is True and message.content.startswith(prefix+"prefix") is False:

				sql = "SELECT prefix FROM `prefix` WHERE server_id={0}"
				sql = sql.format(message.guild.id)
				result = self.cursor.execute(sql).fetchall()
				if result:
					prefix = result[0]["prefix"].lower()
			#print(prefix)
			return prefix
		except Exception as e:
			self.cursor.rollback()
			return "$"

	@asyncio.coroutine
	def get_prefix2(self, message, inputprefix):
		"""|coro|
		Retrieves the prefix the bot is listening to
		with the message as a context.
		Parameters
		-----------
		message: :class:`discord.Message`
			The message context to get the prefix of.
		Raises
		--------
		:exc:`.ClientException`
			The prefix was invalid. This could be if the prefix
			function returned None, the prefix list returned no
			elements that aren't None, or the prefix string is
			empty.
		Returns
		--------
		Union[List[str], str]
			A list of prefixes or a single prefix that the bot is
			listening for.
		"""
		prefix = ret = inputprefix
		if callable(prefix):
			ret = prefix(self.bot, message)
			if asyncio.iscoroutine(ret):
				ret = yield from ret

		if isinstance(ret, (list, tuple)):
			ret = [p for p in ret if p]

		if not ret:
			raise discord.ClientException('invalid prefix (could be an empty string, empty list, or None)')

		return ret

	@asyncio.coroutine
	def get_context(self, message, prefix, *, cls=Context):
		"""|coro|
		Returns the invocation context from the message.
		This is a more low-level counter-part for :meth:`.process_commands`
		to allow users more fine grained control over the processing.
		The returned context is not guaranteed to be a valid invocation
		context, :attr:`.Context.valid` must be checked to make sure it is.
		If the context is not valid then it is not a valid candidate to be
		invoked under :meth:`~.Bot.invoke`.
		Parameters
		-----------
		message: :class:`discord.Message`
			The message to get the invocation context from.
		cls
			The factory class that will be used to create the context.
			By default, this is :class:`.Context`. Should a custom
			class be provided, it must be similar enough to :class:`.Context`\'s
			interface.
		Returns
		--------
		:class:`.Context`
			The invocation context. The type of this can change via the
			``cls`` parameter.
		"""

		view = StringView(message.content)
		ctx = cls(prefix=None, view=view, bot=self.bot, message=message)

		if self.bot._skip_check(message.author.id, self.bot.user.id):
			return ctx

		prefix = yield from self.bot.get_prefix(message, prefix)
		invoked_prefix = prefix

		if isinstance(prefix, str):
			if not view.skip_string(prefix):
				return ctx
		else:
			invoked_prefix = discord.utils.find(view.skip_string, prefix)
			if invoked_prefix is None:
				return ctx

		invoker = view.get_word().lower()
		ctx.invoked_with = invoker
		ctx.prefix = invoked_prefix
		ctx.command = self.bot.all_commands.get(invoker)
		ctx.personality = yield from self.getPersonality(message)
		return ctx

	@asyncio.coroutine
	def process_commands(self, message, prefix):
		"""|coro|
		This function processes the commands that have been registered
		to the bot and other groups. Without this coroutine, none of the
		commands will be triggered.
		By default, this coroutine is called inside the :func:`.on_message`
		event. If you choose to override the :func:`.on_message` event, then
		you should invoke this coroutine as well.
		This is built using other low level tools, and is equivalent to a
		call to :meth:`~.Bot.get_context` followed by a call to :meth:`~.Bot.invoke`.
		Parameters
		-----------
		message : discord.Message
			The message to process commands for.
		"""
		ctx = yield from self.bot.get_context(message,prefix)
		yield from self.bot.invoke(ctx)
