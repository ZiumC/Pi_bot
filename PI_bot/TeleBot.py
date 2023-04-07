import sys
import os
import time
import datetime
import schedule
import telepot
import PublicCommands
from OwnersCommands import Admin
from telepot.loop import MessageLoop

# your telegram ID
OWNERS_ID = []
# your telegram bot API KEY
bot = telepot.Bot('')

# telegram bot can handle with 4096 message length
# i recommend that to leave this value at 3800
MAX_LENGTH_OF_MESSAGE = 3800


# specify output path for log here
path_to_bot_log = ""

# if you want to mine your log with sshd service just put path here
path_to_log = ""

# put here your name which you are using in SFTP
users = ['pi']
admin = Admin(path_to_bot_log, path_to_log, MAX_LENGTH_OF_MESSAGE, users)


def redirect_std_out():
    sys.stdout.flush()
    os.system(path_to_bot_log)


# every thing starts here
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    user_id = msg['from']['id']

    split_command = command.split(" ")
    command_type = split_command[0]
    command_mode = ""
    status = "FAILED "

    if OWNERS_ID.__contains__(user_id):

        if len(split_command) > 1:
            command_mode = split_command[1]
        status = admin.process_command(user_id, chat_id, bot, command_type, command_mode)

    else:
        status = PublicCommands.public_commands(user_id, chat_id, bot, command_type)

    print(' {},       {},      {},     {},     {} '
          .format(datetime.date.today(), chat_id, user_id, status, command))


MessageLoop(bot, handle).run_as_thread()
# ################# DO NOT DELETE THIS LINE #################
redirect_std_out()
print("I am listening since {}...".format(datetime.date.today()))
print('     Date,           User,          Chat id,      Status,     Command')

while 1:
    schedule.run_pending()
    time.sleep(100)
