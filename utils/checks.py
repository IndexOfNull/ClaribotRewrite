from discord.ext import commands
import discord.utils

class No_Owner(commands.CommandError): pass
class No_Perms(commands.CommandError): pass
class No_Role(commands.CommandError): pass
class No_Admin(commands.CommandError): pass
class No_Mod(commands.CommandError): pass
class No_Sup(commands.CommandError): pass
class No_ServerandPerm(commands.CommandError): pass
class Nsfw(commands.CommandError): pass
class No_Special(commands.CommandError): pass

bot_owner = 166206078164402176

special_users = [179714881526824960,219938711264165909,158057952085934080,158058382799011840,391373731852976139,158057812054769665] #Ev, Cad, Mil, Dan, Grnt, Mt 

def is_special():
	def predicate(ctx):
		user = ctx.message.author.id
		if user in special_users or user == bot_owner:
			return True
		else:
			raise No_Special()
	return commands.check(predicate)

def is_owner_check(message):
	if message.author.id == bot_owner:
		return True
	raise No_Owner()

def is_bot_owner():
	return commands.check(lambda ctx: is_owner_check(ctx.message))

def check_permissions(ctx,perms):
	if len(perms) == 0:
		return False
	msg = ctx.message
	if msg.author.id == bot_owner:
		return True
	ch = msg.channel
	permissions = ch.permissions_for(msg.author)
	print(getattr(permissions, perm, None) == value for perm, value in perms.items())
	return all(getattr(permissions, perm, None) == value for perm, value in perms.items())

def role_or_perm(t, ctx, check, **perms):
	print(perms)
	if check_permissions(ctx,perms):
		print("check perms")
		return True
	msg = ctx.message
	ch = msg.channel
	author = msg.author
	if not isinstance(ctx.message.channel, discord.TextChannel):
		return False
	role = discord.utils.find(check, author.roles)
	if role is not None:
		return True
	if t:
		return False
	else:
		raise No_Role()


admin_roles = ("admin","administrator","boss","god","owner","boss")
admin_perms = ['administrator', 'manage_guild']
def admin_or_perm(**perms):
	def predicate(ctx):
		if not isinstance(ctx.message.channel, discord.TextChannel):
			return True
		if ctx.message.author.id == ctx.message.guild.owner.id:
			return True
		if role_or_perm(True, ctx, lambda r: r.name.lower() in admin_roles, **perms):
			print("role_or_perm")
			return True
		for role in ctx.message.author.roles:
			role_perms = []
			for perm in role.permissions:
				role_perms.append(perm)
			for perm in role_perms:
				for perm2 in admin_perms:
					if perm[0] == perm2 and perm[1] == True:
						return True
		raise No_Admin()
	return commands.check(predicate)

mod_perms = ['manage_messages', 'ban_members', 'kick_members']
mod_roles = ('mod', 'moderator')
def mod_or_perm(**perms):
	def predicate(ctx):
		if not isinstance(ctx.message.channel, discord.TextChannel):
			return True
		if ctx.message.author.id == ctx.message.guild.owner.id:
			return True
		if role_or_perm(True, ctx, lambda r: r.name.lower() in mod_roles, **perms):
			return True
		for role in ctx.message.author.roles:
			role_perms = []
			for perm in role.permissions:
				role_perms.append(perm)
			for perm in role_perms:
				for perm2 in mod_perms:
					if perm[0] == perm2 and perm[1] == True:
						return True
				for perm2 in admin_perms:
					if perm[0] == perm2 and perm[1] == True:
						return True
		raise No_Mod()
	return commands.check(predicate)

def is_admin(message):
	if not isinstance(message.channel, discord.TextChannel):
		return True
	if message.author.id == message.guild.owner.id:
		return True
	for role in message.author.roles:
		if role.name.lower() in admin_roles:
			return True
		role_perms = []
		for perm in role.permissions:
			role_perms.append(perm)
		for perm in role_perms:
			for perm2 in admin_perms:
				if perm[0] == perm2 and perm[1] == True:
					return True
	return False

def nsfw():
	def predicate(ctx):
		channel = ctx.message.channel
		if not isinstance(channel, discord.TextChannel):
			return True
		if channel.is_nsfw():
			return True
		else:
			raise Nsfw()
	return commands.check(predicate)
