import asyncio
import datetime
import sys, os
import argparse
import json
from bot import Claribot

with open("bot.json","r") as r:
    settings = json.loads(r.read())

parser = argparse.ArgumentParser(description='Runs the bot with the specified shard count and shard id')
parser.add_argument('-d','--dev',help="Starts the bot in developer mode",nargs=2,metavar=("shard_id","shard_count"))

args = parser.parse_args()

loop = asyncio.get_event_loop()

db_pswd = settings["db_pswd"]
token = settings["token"]

if args.dev:
	dev_mode = True
else:
	dev_mode = False

shard_id = [int(s) for s in os.path.realpath(__file__) if s.isdigit()][0]
shard_count = len([s for s in os.listdir() if s.startswith('main') and s[4].isdigit()])

if dev_mode:
	shard_count = int(args.dev[1])
	shard_id = int(args.dev[0])

print("SHARD ID: " + str(shard_id) + ", SHARD COUNT: " + str(shard_count))

bot = Claribot(loop=loop,shard_id=shard_id,shard_count=shard_count,dev_mode=dev_mode,max_messages=10000,db_pswd=db_pswd,token=token)

if __name__ == "__main__":
	try:
		task = loop.create_task(bot.run())
		task.add_done_callback(functools.partial(main, loop))
		bot.own_task = task
		#loop.create_task(watcher())
		loop.run_until_complete(task)
		loop.run_forever()
	except (KeyboardInterrupt, RuntimeError):
		print('\nKeyboardInterrupt - Shutting down...')
		bot.die()
	finally:
		print('--Closing Loop--')
		loop.close()
