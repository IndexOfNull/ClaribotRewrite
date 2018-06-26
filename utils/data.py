#Data.py: A place deticated to data. This should make it easy to quickly add, remove, or edit large sets of data without having to sift through code.
#Sidenote: All new functions involving data retrieval or manipulation (excluding API and stuff like datetimes) will be put here. This is to organize functions better.

import discord

class Data(): #A class that contains data from all classes.

	def __init__(self,bot):
		self.bot = bot
		self.AdvCheckData = AdvCheckData(bot)
		self.MiscData = MiscData()

class AdvCheckData():

	def __init__(self,bot):
		self.bot = bot
		self.cursor = self.bot.mysql.cursor

	def deleteSpecialUser(self,user):
		try:
			sql = "DELETE FROM `special_users` WHERE user_id={0.id};".format(user)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except:
			self.cursor.rollback()
			return False

	def addSpecialUser(self,user):
		try:
			sql = "INSERT INTO `special_users` (`user_id`) VALUES ('{0.id}');".format(user)
			result = self.cursor.execute(sql)
			self.cursor.commit()
			return True
		except:
			self.cursor.rollback()
			return False

	def getUserSpecial(self,user):
		try:
			id = user.id
			sql = "SELECT `user_id` FROM `special_users` WHERE user_id={0.id};".format(user)
			results = self.cursor.execute(sql).fetchall()
			if results:
				if results[0]["user_id"] == id:
					return True
				else:
					return False
			else:
				return False
		except Exception as e:
			self.cursor.rollback()
			print(e)
			return False

class MiscData():

	def __init__(self):
		self.InsultTemplates = []

	def get8BallResponses(self):
		responses = [
		"It is certain",
		"It is decidedly so",
		"Without a doubt",
		"Yes, definitely",
		"You may rely on it",
		"As I see it, yes",
		"Most likely",
		"Outlook good",
		"Yes",
		"Signs point to yes",
		"Reply hazy, try again",
		"Ask again later",
		"Better not tell you now",
		"Cannot predict now",
		"Concentrate and ask again",
		"Don't count on it",
		"My reply is no",
		"My sources say no",
		"Outlook not so good",
		"Very doubtful",
		"The answer lies within",
		"That's a question for your parents",
		"Do you think I'm some kind of psychic?",
		"ERROR: Stupid Question Asked"
		]
		return responses

	def getInsultTemplates(self):
		templates = [
		"You are <adjective>",
		"You look like <article target=id> <adjective id=id> <animal>",
		"Everyone thinks you are <animal> <animal_part>",
		"	You are as <adjective> as <article target=adj1> <adjective min=1 max=3 id=adj1> <amount> of <adjective min=1 max=3> <animal> <animal_part>"
		]
		return templates

	def getWholesomeResponses(self):
		responses = [
			"You could open that jar of mayonnaise using only 3 fingers.",
			"Strangers all wanna sit next to you on the bus.",
			"Coworkers fantasizes about getting stuck in the elevator with you.",
			"If Einstein could meet you, he'd be \"mildly to moderately\" intimidated.",
			"At least two friends are going to name their child and/or goldfish after you.",
			"socks + sandals + you = I'm into it.",
			"Your ex thought about you this morning, then they thought about donuts.",
			"You are freakishly good at thumb wars.",
			"A 3rd tier cable network would totally create a television show about you.",
			"The FBI tapped your phone just to hear the sound of your voice.",
			"You remind everyone of kiwis- delicious and surprisingly fuzzy.",
			"You never forget to fill the ice-cube tray.",
			"People enjoy you accidentally touching their butt while putting on your seat-belt.",
			"I’d give you the last piece of my gum even if I’d just ate garlic.",
			"There was a high school rumor that you are a distant relative of Abraham Lincoln.",
			"You could make up a weird religion or diet and everyone would follow it.",
			"Your siblings are pissed that your photo is the star of your parent's mantle.",
			" Everyone at sleepovers thought you were the bravest during thunderstorms.",
			"A doctor once saw your butt through the hospital gown. They approve!",
			"Someone almost got a tattoo of your name once, but their mom talked them out of it.",
			"You are your parent's greatest accomplishment, unless they invented the \"spork\".",
			"Some dudes hope you start a band so they can start a cover band of that band.",
			"Your principal would call you to the office just to look cool.",
			"Your allergies are some of the least embarrassing allergies.",
			"Your handshake conveys intelligence, confidence and minor claminess.",
			"Cops admire your ability to stay a perfect 3-5 miles above the speed limit.",
			"You rarely have to go to the bathroom when you fly in the window seat.",
			"Your roommate wants a lock of your hair but is afraid to ask.",
			"Cockroaches, mice and other pests avoid your place out of respect.",
			"Callers are intimidated by how funny your voicemail greeting is.",
			"Kids think you are the “cool old person”.",
			"People always think your jeggings are regular jeans.",
			"80% of motorcycle gangs think you’d be a delightful sidecar.",
			"Everyone at the laundromat thinks you have the cutest underwear.",
			"People behind you at movies think you are the perfect height.",
			"Your parents argue over which one of them you look like.",
			"Sushi chefs are wowed by your chopstick dexterity.",
			"You want the best for everyone...except Gary.",
			"You are someone's \"the one that got away\".",
			"Everybody wants to invite you to their Discord server.",
			"You are the pride of your home town.",
			"The world loves you."
		]
		return responses
