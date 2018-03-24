import asyncio
from discord.ext import commands
import discord
from utils import checks
from random import *
import hashlib
from sqlalchemy.sql import text

class Utility():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = bot.mysql.cursor
		self.getPersonality = self.bot.funcs.getPersonality
		self.getCommandMessage = self.bot.funcs.getCommandMessage
		self.getGlobalMessage = self.bot.funcs.getGlobalMessage

	@commands.command()
	@commands.cooldown(1,2,commands.BucketType.user)
	async def help(self,ctx):
		await ctx.send(ctx.message.author.mention + " https://github.com/IndexOfNull/ClaribotRewrite/blob/master/Commands.txt")

	@commands.group()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	async def blacklist(self,ctx):
	    if ctx.invoked_subcommand is None:
	        await ctx.send('Invalid subcommand passed...')



	@blacklist.command(pass_context=True)
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_channels=True)
	async def channel(self,ctx,channel:discord.TextChannel=None):
		personality = ctx.personality
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		wait = await ctx.send(msg)
		await ctx.channel.trigger_typing()
		if channel is None:
			print("no channel")
			channel = ctx.channel
		if channel not in ctx.message.guild.channels:
			return
		blacklisted = False
		sql = "SELECT channel_id FROM `blacklist_channels` WHERE channel_id={0}".format(channel.id)
		result = self.cursor.execute(sql).fetchall()
		print(result)
		if result:
			print(str(result[0]["channel_id"]) + " == " + str(channel.id))
			if result[0]["channel_id"] == channel.id:
				blacklisted = True
		if blacklisted is True:
			sql = "DELETE FROM `blacklist_channels` WHERE channel_id={0}".format(channel.id)
			msg = (await self.getCommandMessage(personality, ctx, "remove_blacklist", "blacklist-channel")).format(channel.mention)
		else:
			sql = "INSERT INTO `blacklist_channels` (`server_id`, `channel_id`) VALUES ('{0}', '{1}')".format(channel.guild.id,channel.id)
			msg = (await self.getCommandMessage(personality, ctx, "added_blacklist", "blacklist-channel")).format(channel.mention)
		result = self.cursor.execute(sql)
		self.cursor.commit()
		await wait.delete()
		await ctx.send(msg)

	@blacklist.command(pass_context=True)
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(mute_members=True)
	async def user(self,ctx,user:discord.Member):
		personality = ctx.personality
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		wait = await ctx.send(msg)
		await ctx.channel.trigger_typing()
		blacklisted = False
		sql = "SELECT user_id FROM `blacklist_users` WHERE user_id={0} AND server_id={1}".format(user.id,ctx.message.guild.id)
		result = self.cursor.execute(sql).fetchall()
		if result:
			if result[0]["user_id"] == user.id:
				blacklisted = True
		if blacklisted is True:
			sql = "DELETE FROM `blacklist_users` WHERE user_id={0} AND server_id={1}".format(user.id,ctx.message.guild.id)
			msg = (await self.getCommandMessage(personality, ctx, "remove_blacklist", "blacklist-user")).format(user.name)
		else:
			sql = "INSERT INTO `blacklist_users` (`server_id`, `user_id`) VALUES ('{0}', '{1}')".format(ctx.channel.guild.id,user.id)
			msg = (await self.getCommandMessage(personality, ctx, "added_blacklist", "blacklist-user")).format(user.name)
		result = self.cursor.execute(sql)
		self.cursor.commit()
		await wait.delete()
		await ctx.send(msg)

	@commands.command(pass_context=True)
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def prefix(self, ctx, *, txt:str=None):
		personality = ctx.personality
		if len(txt) > 10:
			await ctx.send((await self.getCommandMessage(personality,ctx,"input_too_big")).format(10))
			return
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		wait = await ctx.send(msg)
		await ctx.channel.trigger_typing()
		sql = "SELECT prefix FROM `prefix` WHERE server_id={0}"
		sql = sql.format(ctx.message.guild.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			server_prefix = "$"
		else:
			server_prefix = result[0]["prefix"]
		if txt is None:
			msg = (await self.getCommandMessage(personality, ctx, "current_prefix")).format(server_prefix)
			await wait.delete()
			await ctx.send(msg)
			return
		else:
			if txt.lower() != server_prefix:
				if len(result) == 0:
					sql = "INSERT INTO `prefix` (`server_id`, `prefix`) VALUES ('{0}', :prefix)".format(ctx.message.guild.id)
				else:
					sql = 'UPDATE `prefix` SET prefix= :prefix WHERE server_id={0}'.format(ctx.message.guild.id)
				result = self.cursor.execute(sql, {"prefix": txt.lower()})
				self.cursor.commit()
			msg = (await self.getCommandMessage(personality, ctx, "set_prefix")).format(txt.lower())
			await wait.delete()
			await ctx.send(msg)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def warn(self,ctx,user:discord.Member,*,txt:str):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			embed = discord.Embed(title="Server Warning",type="rich",color=discord.Color.red())
			embed.add_field(name="Server",value="{0.name} ({0.id})".format(ctx.guild),inline=True)
			embed.add_field(name="Warned By",value=ctx.author.mention,inline=True)
			embed.add_field(name="Timestamp",value=(await self.bot.funcs.getCurrentFormattedTime()),inline=False)

			currenttime = str(str((await self.bot.funcs.getUTCNow())) + " " + str(randint(0,1000))).encode("utf-8")
			hashed = str(hashlib.sha1(currenttime).hexdigest())[:6]
			embed.add_field(name="Issue ID",value=hashed,inline=True)
			embed.add_field(name="Reason",value=txt,inline=False)
			embed.set_footer(text="You may be able to contact an admin about this incident. You may also need to provide the given issue id.")
			#sql = "INSERT INTO `warnings` (`server_id`, `user_id`, `reason`, `warner`, `timestamp`, `issue_id`) VALUES ('{0.guild.id}', '{1}', '{2}', '{3}', '{4}', '{5}');".format(ctx,user.id,txt,ctx.author.id,(await self.bot.funcs.getUTCNow()),hashed)
			sql = text("INSERT INTO `warnings` (`server_id`, `user_id`, `reason`, `warner`, `timestamp`, `issue_id`) VALUES ('{0.guild.id}', '{1}', :reason, '{2}', '{3}', '{4}');".format(ctx,user.id,ctx.author.id,(await self.bot.funcs.getUTCNow()),hashed))
			#sql = "INSERT INTO `warnings` (`server_id`, `user_id`, `reason`, `warner`, `timestamp`, `issue_id`) VALUES (':guild', ':user_id', ':reason', ':warner', ':timestamp', ':issue_id');"
			self.cursor.execute(sql, {"reason":txt})
			self.cursor.commit()
			await wait.delete()
			await user.send(embed=embed)
			msg = (await self.getCommandMessage(ctx.personality,ctx,"sent")).format(user)
			await ctx.send(msg)
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def warnhistory(self,ctx,user:discord.Member):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			sql = "SELECT * FROM `warnings` WHERE server_id={0.id} AND user_id={1.id} ORDER BY `timestamp` DESC".format(ctx.message.guild,user)
			result = self.cursor.execute(sql).fetchall()
			sql2 = "SELECT `issue_id` FROM `warnings` WHERE server_id!={0.id} AND user_id={1.id}".format(ctx.message.guild,user)
			result2 = self.cursor.execute(sql2).fetchall()
			clean = True
			finalmsg = (await self.getCommandMessage(ctx.personality,ctx,"clean_full")).format(user)
			if result:
				finalmsg = "Showing warning history for user **{0.name}#{0.discriminator}**\n".format(user)
				listentry = "\n{0}: {1}, ID: `{2}`"
				warnings = result[:5]
				for idx,warning in enumerate(warnings):
					utc = (await self.bot.funcs.secondsToUTC(warning["timestamp"]))
					timestamp = (await self.bot.funcs.getFormattedTime(utc))
					finalmsg += listentry.format(idx+1, timestamp, warning["issue_id"])
				if result2:
					finalmsg += "\n\n" + (await self.getCommandMessage(ctx.personality,ctx,"clean_partial_notice"))
			#THIS IF STATEMENT NEEDS SOME LOVE
			if result2 and not result:
				finalmsg = (await self.getCommandMessage(ctx.personality,ctx,"clean_partial")).format(user,ctx.message.guild)

			await ctx.message.author.send(finalmsg)
			await ctx.send((await self.getCommandMessage(ctx.personality,ctx,"sent")).format(ctx.message.author,user))
			await wait.delete()
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def getwarning(self,ctx,warning_id:str):
		wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			sql = "SELECT * FROM `warnings` WHERE server_id={0.id} AND issue_id='{1}'".format(ctx.message.guild,warning_id)
			result = self.cursor.execute(sql).fetchall()[0]

			if result:
				embed = discord.Embed(title="Server Warning",type="rich",color=discord.Color.red())
				embed.add_field(name="Server",value="{0.name} ({0.id})".format(ctx.guild),inline=True)
				print("good")
				embed.add_field(name="Warned By",value=self.bot.get_user(result["warner"]).mention,inline=True)
				print("good")
				utc = (await self.bot.funcs.secondsToUTC(result["timestamp"]))
				print("good")
				timestamp = (await self.bot.funcs.getFormattedTime(utc))
				embed.add_field(name="Timestamp",value=timestamp,inline=False)
				embed.add_field(name="Issue ID",value=result["issue_id"],inline=True)
				embed.add_field(name="Reason",value=result["reason"],inline=False)
				embed.set_footer(text="This is not a real warning, just a mere recreation")
				await ctx.message.author.send(embed=embed)
				await ctx.send((await self.getCommandMessage(ctx.personality,ctx,"sent")).format(ctx.message.author,result["issue_id"]))
			elif not result:
				await ctx.send((await self.getCommandMessage(ctx.personality,ctx,"error")).format(ctx.message.author,user))
			await wait.delete()
		except Exception as e:
			await wait.edit(content="`{0}`".format(e))
			print(e)

	@commands.command()
	@commands.cooldown(1,3)
	@commands.guild_only()
	@checks.mod_or_perm(manage_messages=True)
	async def delwarning(self,ctx,warning_id:str):
		confirmed = await self.bot.funcs.confirm_command(ctx)
		if not confirmed:
			return
		#wait = await ctx.send((await self.bot.getGlobalMessage(ctx.personality,"command_wait")))
		try:
			await ctx.trigger_typing()
			sql = "DELETE FROM `warnings` WHERE server_id={0.id} AND issue_id='{1}'".format(ctx.message.guild,warning_id)
			result = self.cursor.execute(sql)
			if result.rowcount == 0:
				msg = (await self.getCommandMessage(ctx.personality,ctx,"error"))
				await ctx.send(content=msg)
				return
			self.cursor.commit()
			await ctx.send((await self.getCommandMessage(ctx.personality,ctx,"deleted")).format(warning_id))
		except Exception as e:
			await ctx.send(content="`{0}`".format(e))
			print(e)



	@commands.command(pass_context=True)
	@commands.cooldown(1,3,commands.BucketType.guild)
	@commands.guild_only()
	@checks.admin_or_perm(manage_server=True)
	async def personality(self,ctx,txt:str=None):
		personality = ctx.personality
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		wait = await ctx.send(msg)
		await ctx.channel.trigger_typing()
		sql = "SELECT personality FROM `personality` WHERE server_id={0}".format(ctx.message.guild.id)
		result = self.cursor.execute(sql).fetchall()
		if txt is None:
			if len(result) == 0:
				personality = "default"
			else:
				personality = result[0]["personality"]
			msg = (await self.getCommandMessage(personality, ctx, "current_personality")).format(personality)
			await wait.delete()
			await ctx.send(msg)
		else:
			personalities = self.bot.messages
			keys = personalities.keys()
			if not txt.lower() in keys:
				formatted_list =  ', '.join(map(str, list(keys)))
				msg = (await self.getCommandMessage(personality, ctx, "invalid_personality")).format(formatted_list)
				await wait.delete()
				await ctx.send(msg)
				return
			if personality != txt.lower():
				if len(result) == 0:
					sql = "INSERT INTO `personality` (`server_id`, `personality`) VALUES ('{0}', '{1}')".format(ctx.message.guild.id,txt.lower())
				else:
					sql = 'UPDATE `personality` SET personality={0} WHERE server_id={1}'.format('"'+txt.lower()+'"',ctx.message.guild.id)
				result = self.cursor.execute(sql)
				self.cursor.commit()
			msg = (await self.getCommandMessage(personality, ctx, "set_personality")).format(txt.lower())
			await wait.delete()
			await ctx.send(msg)

	@commands.command(pass_context=True,hidden=True)
	@checks.is_bot_owner()
	@commands.cooldown(1,5)
	async def exec(self, ctx, *, code:str):
		code = code.strip('` ')
		python = '```py\n{}\n```'
		result = None
		variables = {
			'bot': self.bot,
			'ctx': ctx,
			'message': ctx.message,
			'server': ctx.message.guild,
			'channel': ctx.message.channel,
			'author': ctx.message.author
		}
		try:
			result = exec(code, variables)
		except Exception as e:
			await ctx.message.channel.send(python.format(type(e).__name__ + ': ' + str(e)))
			return
		if asyncio.iscoroutine(result):
			result = await result
		#"```markdown\nUSE THIS WITH EXTREME CAUTION\n\nEval() Results\n=========\n\n> " + python.format(result)) + "\n```"
		await ctx.message.channel.send(python.format(result))

	@commands.command(pass_context=True,hidden=True)
	@checks.is_bot_owner()
	@commands.cooldown(1,5)
	async def eval(self, ctx, *, code:str):
		code = code.strip('` ')
		python = '```py\n{}\n```'
		result = None
		variables = {
			'bot': self.bot,
			'ctx': ctx,
			'message': ctx.message,
			'server': ctx.message.guild,
			'channel': ctx.message.channel,
			'author': ctx.message.author
		}
		try:
			result = eval(code, variables)
		except Exception as e:
			await ctx.message.channel.send(python.format(type(e).__name__ + ': ' + str(e)))
			return
		if asyncio.iscoroutine(result):
			result = await result
		#"```markdown\nUSE THIS WITH EXTREME CAUTION\n\nEval() Results\n=========\n\n> " + python.format(result)) + "\n```"
		await ctx.message.channel.send(python.format(result))

	@commands.command(pass_context=True,aliases=["playing"])
	@checks.is_bot_owner()
	@commands.cooldown(1,5)
	async def status(self, ctx, *, motd:str):
		await self.bot.change_presence(activity=discord.Game(name=motd))
		sql = "UPDATE `bot_data` SET value= :motd WHERE var_name='playing'"
		self.cursor.execute(sql, {"motd": motd})
		self.cursor.commit()
		msg = await ctx.message.channel.send(await self.getCommandMessage(ctx.personality,ctx,"success"))
		await asyncio.sleep(5)
		await msg.delete()
		print("MOTD changed to: " + motd)

def setup(bot):
	bot.add_cog(Utility(bot))


lol = "4"
def add(sum1,sum2):
	return sum1 + sum2
