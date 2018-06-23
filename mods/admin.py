import asyncio
from discord.ext import commands
import discord
from utils import checks
from random import *
import hashlib
from sqlalchemy.sql import text
from io import BytesIO, StringIO
import json
import sys, os

class Admin():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = bot.mysql.cursor
		self.funcs = bot.funcs
		self.getPersonality = self.bot.funcs.getPersonality
		self.getCommandMessage = self.bot.funcs.getCommandMessage
		self.getGlobalMessage = self.bot.funcs.getGlobalMessage
		self.chatbot = self.bot.chatbot

	@commands.command()
	@checks.admin_or_perm(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	@commands.guild_only()
	async def idban(self,ctx,*ids:int):
		try:
			confirmed = await self.bot.funcs.confirm_command(ctx)
			if not confirmed:
				return
			success = []
			failed = False
			for id in ids:
				if isinstance(id, int):
					user = self.bot.get_user(id)
					if user:
						await ctx.guild.ban(user,reason="Banned by {0.name} using the $idban command".format(ctx.message.author),delete_message_days=0)
						success.append(user)
					else:
						failed = True
				else:
					failed = True
			if failed == True and success:
				await ctx.send(await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"user_error"))
				return
			elif failed == True:
				await ctx.send(await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error"))
				return
			if success:
				await ctx.send(await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success"))
				return
		except Exception as e:
			print(e)
			await ctx.send(await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error"))


	@commands.group(invoke_without_command=True)
	@commands.cooldown(1,5,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	@commands.bot_has_permissions(manage_messages=True)
	async def prune(self,ctx,num:int=None,user:discord.User=None):
		try:
			numlimit = 100
			if ctx.invoked_subcommand is None and num is None:
				await ctx.send('Valid subcommands are `bots, attachments, embeds, images, with`')
			elif not num is None:
				if num > numlimit:
					await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
					return
				counter = 0
				async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
					if not user is None:
						if elem.author == user:
							await elem.delete()
					else:
						await elem.delete()
					counter+=1
				if counter == 0:
					await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
				elif user is not None:
					await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success_user","prune-messages")).format(counter,user))
				else:
					await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))

	@commands.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def clean(self,ctx,num:int):
		try:
			numlimit = 100
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			commands = []
			for cmd in self.bot.commands:
				commands.append(cmd.name)
				for alias in cmd.aliases:
					commands.append(cmd.name)
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				if elem.content.startswith("$") and elem.content.split(" ")[0][1:] in commands:
					await elem.delete()
				elif elem.author.id == self.bot.user.id:
					await elem.delete()
					counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success")).format(counter))
		except Exception as e:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error")))

	@prune.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def bots(self,ctx,num:int):
		try:
			numlimit = 100
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				if elem.author.bot is True:
					await elem.delete()
				counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except Exception as e:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))

	@prune.command()
	@commands.cooldown(1,20,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def gifs(self,ctx,num:int):
		try:
			numlimit = 25
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				attachments = elem.attachments
				isimage = False
				for attachment in attachments:
					isimage = await self.bot.funcs.imagecheck(attachment.url,gif=True)
					if isimage:
						break
				if isimage:
					await elem.delete()
					counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except Exception as e:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))

	@prune.command(name="with")
	@commands.cooldown(1,20,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def prune_with(self,ctx,num:int,*,text:str):
		try:
			numlimit = 100
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				if text in elem.content:
					await elem.delete()
					counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except Exception as e:
			print(ec)
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))

	@prune.command()
	@commands.cooldown(1,20,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def images(self,ctx,num:int):
		try:
			numlimit = 25
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				attachments = elem.attachments
				isimage = False
				for attachment in attachments:
					isimage = await self.bot.funcs.imagecheck(attachment.url)
					if isimage:
						break
				if isimage:
					await elem.delete()
					counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except Exception as e:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))

	@prune.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def embeds(self,ctx,num:int):
		try:
			numlimit = 100
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				if len(elem.embeds) >= 1:
					await elem.delete()
					counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except Exception as e:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))

	@prune.command()
	@commands.cooldown(1,5,commands.BucketType.guild)
	@checks.mod_or_perm(manage_messages=True)
	@commands.guild_only()
	async def attachments(self,ctx,num:int):
		try:
			numlimit = 100
			if num > numlimit:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"message_limit","prune-messages")).format(numlimit))
				return
			counter = 0
			async for elem in ctx.message.channel.history(limit=num,before=ctx.message):
				if len(elem.attachments) >= 1:
					await elem.delete()
					counter+=1
			if counter == 0:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"no_messages","prune-messages")))
			else:
				await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"success","prune-messages")).format(counter))
		except Exception as e:
			await ctx.send((await self.bot.funcs.getCommandMessage(ctx.personality,ctx,"error","prune-messages")))


def setup(bot):
	bot.add_cog(Admin(bot))
