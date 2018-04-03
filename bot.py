import asyncio
import datetime
import sys, os
import discord
import re
import logging
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from discord.ext import commands
import discord
from utils.funcs import Funcs
from utils import checks
import time
from random import *

modules = [
"mods.util",
"mods.fun",
"mods.misc",
"mods.nsfw"
]



current_milli_time = lambda: int(round(time.time() * 1000))

def get_personality_info():
	messages = None
	defaultmessages = None
	with open("messages.json","r") as f:
		messages = json.loads(f.read())
	#with open("defaultmessages.json","r") as f:
	#	defaultmessages = json.dumps(f.read())
	return (defaultmessages,messages)

def init_logging(shard_id, bot):
	mode = logging.INFO
	logging.root.setLevel(mode)
	logger = logging.getLogger('Claribot #{0}'.format(shard_id))
	logger.setLevel(mode)
	log = logging.getLogger()
	log.setLevel(mode)
	handler = logging.FileHandler(filename='claribot_{0}.log'.format(shard_id), encoding='utf-8', mode='a')
	log.addHandler(handler)
	bot.logger = logger
	bot.log = log

class Object(object):
	pass

def init_funcs(bot):
	if bot.dev_mode is True:
		db_name = "Claribot_dev"
	else:
		db_name = "Claribot"
	global cursor, engine, Session
	engine = create_engine("mysql+pymysql://{0}:{1}@localhost/{2}?charset=utf8mb4".format("claribot"+str(bot.shard_id),bot.db_pswd,db_name),isolation_level="READ COMMITTED")
	session_factory = sessionmaker(bind=engine)
	Session = scoped_session(sessionmaker(bind=engine))
	bot.mysql = Object()
	engine = bot.mysql.engine = engine
	cursor = bot.mysql.cursor = bot.get_cursor
	bot.remove_command("help")
	funcs = Funcs(bot,cursor)
	bot.funcs = funcs
	bot.process_commands = funcs.process_commands
	bot.get_context = funcs.get_context
	bot.get_prefix = funcs.get_prefix2
	bot.getBlacklisted = funcs.getBlacklisted
	bot.getGlobalMessage = funcs.getGlobalMessage
	bot.getCommandMessage = funcs.getCommandMessage
	bot.get_images = funcs.get_images
	personality_info = get_personality_info()
	bot.defaultmessages = personality_info[0]
	bot.messages = personality_info[1]


class Claribot(commands.Bot):
	def __init__(self, *args, **kwargs):
		if sys.platform == "win32":
			self.loop = kwargs.pop('loop', asyncio.ProactorEventLoop())
			asyncio.set_event_loop(self.loop)
		else:
			self.loop = kwargs.pop('loop', asyncio.get_event_loop())
			asyncio.get_child_watcher().attach_loop(self.loop)
		shard_id = kwargs.get('shard_id', 0)
		command_prefix = kwargs.pop('command_prefix', commands.when_mentioned_or('$'))
		super().__init__(command_prefix=command_prefix, *args, **kwargs)
		self.token = kwargs.pop("token")
		init_logging(shard_id,self)
		self.dev_mode = kwargs.pop("dev_mode",False)
		self.owner = None
		db_pswd = kwargs.pop('db_pswd')
		self.db_pswd = db_pswd
		self.cmd_start = None
		self.confirmation_commands = ["delwarning","deletewarning"]

	async def on_ready(self):
		init_funcs(self)
		for cog in modules:
			try:
				self.load_extension(cog)
			except Exception as e:
				msg = 'Failed to load mod {0}\n{1}: {2}'.format(cog, type(e).__name__, e)
				print(msg)

		playing = self.mysql.cursor.execute("SELECT value FROM `bot_data` WHERE var_name='playing'").fetchall()[0]["value"]
		if not playing:
			playing = "nothing"
		print('------\n{0}\nShard {1}/{2}{3}{4}------'.format(self.user, self.shard_id, self.shard_count-1, '\nDev Mode: Enabled\n' if self.dev_mode else '\n',"Playing: "+playing+"\n"))
		game = discord.Game(name=playing)
		await self.change_presence(activity=game)

	async def command_help(self,ctx):
		if ctx.invoked_subcommand:
			cmd = ctx.invoked_subcommand
		else:
			cmd = ctx.command
		pages = await self.formatter.format_help_for(ctx, cmd)
		for page in pages:
			await ctx.message.channel.send(page.replace("\n", "fix\n", 1))

	async def stress_test(self,message,prefix):
		print("COMMANDING!")
		current_time = date.datetime().microsecond / 1000
		await self.process_commands(message,prefix)
		done_time = date.datetime().microsecond / 1000
		print("Done in {0}ms".format(done_time-current_time))

	async def handle_points(self,message):
		dice = randint(1,3)
		user = message.author
		if dice == 1:

			print("handling points")
			current_time = await self.funcs.getUTCNow()
			points_row = await self.funcs.get_points(user,message.guild)
			#print(str(points_row["points"]) + ", " + str(points_row["timestamp"]))
			good = False
			is_none = False
			if points_row is False:
				print("ERROR")
				return
			if points_row:
				good = True
				if "no_row" in points_row:
					is_none = True
			if good:
				extra_points = True
				msg_count = 0
				def predicate(msg):
					return msg.author.id != message.author.id and not msg.author.bot
				history = await message.channel.history(limit=10,before=message).filter(predicate).flatten()
				print(history)
				if not history:
					history = [message]
					extra_points = False
				def extrapredicate(msg):
					return msg.author.id == message.author.id and message.author.bot is False
				print("exra_points: " + str(extra_points))
				if extra_points:
					if not is_none:
						last_time = await self.funcs.secondsToUTC(points_row["timestamp"])
						time_dif = current_time - points_row["timestamp"]
						if not time_dif > 3600:
							return
						async for elem in message.channel.history(limit=10,around=last_time).filter(extrapredicate):
							msg_count += 1
					print(history[0].content)
					async for elem in message.channel.history(limit=25,before=history[0]).filter(extrapredicate):
						msg_count += 1
				#print("giving points")
				await self.funcs.give_points(user,20+int(0.4*msg_count),message.guild,message)
				return
			print("Did not meet all requirements")



	async def on_message(self, message):
		await self.wait_until_ready()
		if self.owner is None:
			application_info = await self.application_info()
			self.owner = application_info.owner
		if self.dev_mode and message.author != self.owner:
			return
		if message.author.bot:
			return
		if isinstance(message.channel, discord.TextChannel):
			await self.handle_points(message)

		prefix_result = await self.funcs.getPrefix(message) #self.get_prefixes(message), could be used for database config
		prefix = prefix_result

		blacklisted = await self.getBlacklisted(message)

		#blacklisted = False
		if blacklisted and not message.content.lower().startswith(prefix+"blacklist"):
			return

		check = True
		if message.content.lower().startswith(prefix) and check and message.content.lower() != prefix:


			prefix_escape = re.escape(prefix)
			message_regex = re.compile(r'('+prefix_escape+r')'+r'[\s]*(\w+)(.*)', re.I|re.X|re.S)
			match = message_regex.findall(message.content)
			if len(match) == 0:
				return
			match = match[0]
			command = match[1].lower()
			message.content = match[0].lower()+command+match[2]
			#confirmed = await self.confirmation_command(message,command)
			#if not confirmed:
			#	return
			"""print("processing command: " + command)
			print(message.guild.id)"""
			"""print("COMMAND!")
			loop = asyncio.get_event_loop()
			tasks = []
			for i in range(1000):
				tasks.append(self.stress_test(message,prefix))
			loop.run_until_complete(asyncio.wait(tasks))
			loop.close()""" #Torture test stuff
			self.cmd_start = current_milli_time()
			await self.process_commands(message,prefix)

	async def on_command_error(self, ctx, e):
		personality = await self.funcs.getPersonality(ctx.message)
		if isinstance(e, commands.CommandNotFound):
			return
		elif isinstance(e, commands.CommandOnCooldown):
			msg = (await self.funcs.getGlobalMessage(personality,"cooldown"))
			await ctx.send(msg)
		elif isinstance(e, checks.No_Owner):
			msg = (await self.funcs.getGlobalMessage(personality,"no_bot_owner"))
			await ctx.send(msg)
		elif isinstance(e, commands.MissingRequiredArgument):
			await self.command_help(ctx)
		elif isinstance(e, commands.BadArgument):
			await self.command_help(ctx)
		elif isinstance(e, checks.No_Mod):
			msg = (await self.funcs.getGlobalMessage(personality,"no_mod"))
			await ctx.send(msg)
		elif isinstance(e, checks.No_Admin):
			msg = (await self.funcs.getGlobalMessage(personality,"no_admin"))
			await ctx.send(msg)
		elif isinstance(e, checks.No_Role):
			msg = (await self.funcs.getGlobalMessage(personality,"no_role"))
			await ctx.send(msg)
		elif isinstance(e, checks.Nsfw):
			msg = (await self.funcs.getGlobalMessage(personality,"no_nsfw"))
			await ctx.send(msg)
		elif isinstance(e, commands.CheckFailure):
			msg = (await self.funcs.getGlobalMessage(personality,"check_failure"))
			await ctx.send(msg)
		elif isinstance(e, discord.errors.Forbidden):
			msg = "I'm missing the necessary permissions for this command"
			await ctx.send(msg)
		else:
			print("ERROR: " + str(e))

	async def on_command_completion(self,ctx):
		done_time = ctx.message.created_at.microsecond / 1000 - datetime.time().microsecond / 1000
		print("command done in {0} ms".format(done_time))

	@property
	def get_cursor(self):
		return Session()

	def run(self):
		super().run(self.token)

	def die(self):
		try:
			self.loop.stop()
			self.loop.run_forever()
		except Exception as e:
			print(e)

#TO DO
"""
	- Setup database support
	- Setup Commands
	- Setup utility functions
"""
