import asyncio
from discord.ext import commands
import discord

class Utility():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = bot.mysql.cursor
		self.getPersonality = self.bot.funcs.getPersonality
		self.getCommandMessage = self.bot.funcs.getCommandMessage
		self.getGlobalMessage = self.bot.funcs.getGlobalMessage

	@commands.command()
	async def test(self,ctx):
		personality = await self.getPersonality(ctx.message)
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		await ctx.send(msg)

	@commands.group()
	@commands.guild_only()
	async def blacklist(self,ctx):
	    if ctx.invoked_subcommand is None:
	        await ctx.send('Invalid subcommand passed...')


	@blacklist.command(pass_context=True)
	#WE NEED A CHECK HERE
	async def channel(self,ctx,channel:discord.TextChannel=None):
		personality = await self.getPersonality(ctx.message)
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		wait = await ctx.send(msg)
		await ctx.channel.trigger_typing()
		if channel is None:
			print("no channel")
			channel = ctx.channel
		if channel not in ctx.message.guild.channels:
			return
		blacklisted = False
		sql = "SELECT channel_id FROM `blacklist` WHERE channel_id={0}".format(channel.id)
		result = self.cursor.execute(sql).fetchall()
		print(result)
		if result:
			print(str(result[0]["channel_id"]) + " == " + str(channel.id))
			if result[0]["channel_id"] == channel.id:
				blacklisted = True
		if blacklisted is True:
			sql = "DELETE FROM `blacklist` WHERE channel_id={0}".format(channel.id)
			msg = (await self.getCommandMessage(personality, ctx, "remove_blacklist", "blacklist-channel")).format(channel.mention)
		else:
			sql = "INSERT INTO `blacklist` (`server_id`, `channel_id`, `user_id`) VALUES ('{0}', '{1}', '0')".format(channel.guild.id,channel.id)
			msg = (await self.getCommandMessage(personality, ctx, "added_blacklist", "blacklist-channel")).format(channel.mention)
		result = self.cursor.execute(sql)
		self.cursor.commit()
		await wait.delete()
		await ctx.send(msg)

	@blacklist.command(pass_context=True)
	#WE NEED A CHECK HERE
	async def user(self,ctx,user:discord.Member):
		personality = await self.getPersonality(ctx.message)
		msg = (await self.getGlobalMessage(personality,"command_wait"))
		wait = await ctx.send(msg)
		await ctx.channel.trigger_typing()
		blacklisted = False
		sql = "SELECT user_id FROM `blacklist` WHERE user_id={0} AND server_id={1}".format(user.id,ctx.message.guild.id)
		result = self.cursor.execute(sql).fetchall()
		if result:
			if result[0]["user_id"] == user.id:
				blacklisted = True
		if blacklisted is True:
			sql = "DELETE FROM `blacklist` WHERE user_id={0} AND server_id={1}".format(user.id,ctx.message.guild.id)
			msg = (await self.getCommandMessage(personality, ctx, "remove_blacklist", "blacklist-user")).format(user.name)
		else:
			sql = "INSERT INTO `blacklist` (`server_id`, `channel_id`, `user_id`) VALUES ('{0}', '0', '{1}')".format(ctx.channel.guild.id,user.id)
			msg = (await self.getCommandMessage(personality, ctx, "added_blacklist", "blacklist-user")).format(user.name)
		result = self.cursor.execute(sql)
		self.cursor.commit()
		await wait.delete()
		await ctx.send(msg)

	@commands.command(pass_context=True)
	@commands.guild_only()
	async def prefix(self, ctx, *, txt:str=None):
		personality = await self.getPersonality(ctx.message)
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
					sql = "INSERT INTO `prefix` (`server_id`, `prefix`) VALUES ('{0}', '{1}')".format(ctx.message.guild.id,txt.lower())
				else:
					sql = 'UPDATE `prefix` SET prefix={0} WHERE server_id={1}'.format('"'+txt.lower()+'"',ctx.message.guild.id)
				result = self.cursor.execute(sql)
				self.cursor.commit()
			msg = (await self.getCommandMessage(personality, ctx, "set_prefix")).format(txt.lower())
			await wait.delete()
			await ctx.send(msg)

	@commands.command(pass_context=True)
	@commands.guild_only()
	async def personality(self,ctx,txt:str=None):
		personality = await self.getPersonality(ctx.message)
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

def setup(bot):
	bot.add_cog(Utility(bot))
