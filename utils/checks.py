from discord.ext import commands
import discord.utils

class No_Role(commands.CommandError): pass

bot_owner = 12345

def check_perms(ctx,perms):
	msg = ctx.message
	if msg.author.id == bot_owner:
		return True
	msg = ctx.message
	ch = msg.channel
	permissions = ch.permissions_for(msg.author)
	if all(getattr(permissions, perm, None) == value for perm, value in perms.items()):
		return True
	return False

def role_or_perm(t,ctx,check,**perms):
	if check_perms(ctx,perms):
		return True
	channel = ctx.message.channel
	msg = ctx.message
	if not isinstance(channel, discord.TextChannel):
		return True
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
	def final(ctx):
		if not isinstance(ctx.message.channel, discord.TextChannel):
			return True
		if ctx.message.author.id == ctx.message.guild.owner.id:
			return True
		if role_or_perm(True, ctx, lambda r: r.name.lower() in admin_roles, **perms):
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
	return commands.check(final)

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
		print(role_perms)
		for perm in role_perms:
			for perm2 in admin_perms:
				if perm[0] == perm2 and perm[1] == True:
					return True
	return False
