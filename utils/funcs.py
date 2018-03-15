from pymysql.converters import escape_item, escape_string, encoders
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandNotFound, CommandError
import asyncio, aiohttp
from discord.ext.commands.view import StringView
from utils import checks

class Funcs():
	def __init__(self,bot,cursor):
		self.bot = bot
		self.cursor = cursor

	async def getPersonality(self,message):
		personality = "default"
		if isinstance(message.channel, discord.TextChannel) is True:
			sql = "SELECT personality FROM `personality` WHERE server_id={0}".format(message.guild.id)
			result = self.cursor.execute(sql).fetchall()
			if result:
				personality = result[0]["personality"]
		return personality

	async def getBlacklisted(self,message):
		blacklisted = False

		if isinstance(message.channel, discord.TextChannel) is True:
			bypass = checks.is_admin(message)
			print(bypass)
			if bypass:
				return False
			sql = "SELECT channel_id FROM `blacklist` WHERE channel_id={0}".format(message.channel.id)
			result = self.cursor.execute(sql).fetchall()
			if result:
				if result[0]["channel_id"] == message.channel.id:
					blacklisted = True
			if not result:
				sql = "SELECT user_id FROM `blacklist` WHERE user_id={0} AND server_id={1}".format(message.author.id,message.guild.id)
				result = self.cursor.execute(sql).fetchall()
				if result:
					if result[0]["user_id"] == message.author.id:
						blacklisted = True

		return blacklisted

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
