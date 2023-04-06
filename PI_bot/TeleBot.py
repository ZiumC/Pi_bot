import random
import sys
import os
import time
import datetime
import schedule
import re
import telepot
from PrimitiveLogger import Log
from enum import Enum
from telepot.loop import MessageLoop

# your telegram ID
OWNERS_ID = []
# your telegram bot API KEY
bot = telepot.Bot('')

# telegram bot can handle with 4096 message length
# i recommend that to leave this value at 3800
MAX_LENGTH_OF_MESSAGE = 3800

time_pattern = "^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"

# if you are using your bot on rasberry pi and you want to log all data from bot
# specify output path here
path_to_bot_log = ""

# if you want to mine your /var/log/auth.log just put path here
path_to_log = ""

# put here your name which you are using in SFTP
users = ['pi']

# if you have more than one name write:
# for 2 users: users_correct_logins_in = {users[0]: [], users[1]: []}
#              users_failed_logins_tries = {users[0]: [], users[1]: []}

# for 3 users: users_correct_logins_in = {users[0]: [], users[1]: [], users[2]: []}
#              users_failed_logins_tries = {users[0]: [], users[1]: [], users[2]: []}
# and so on...
users_correct_logins_in = {users[0]: []}
users_failed_logins_tries = {users[0]: []}
other_invalid_tries = []


class Unauthorized(Enum):
    ROLL = '/roll'
    TIME = '/time'
    ID = '/id'


class Authorized(Enum):
    SELF = '/self'
    AUTH = '/auth'
    STATS = '/stats'
    STATS_TIME = '/stats_time'
    STATS_JOBS = '/stats_jobs'
    STATS_CANCEL = '/stats_cancel'


def redirect_std_out():
    sys.stdout.flush()
    os.system(path_to_bot_log)


def owners_commands(user_id, chat_id, command_type, command_mode):
    if command_type == Authorized.SELF.value:
        bot.sendMessage(chat_id, "Reading raw log file...")
        raw_log = Log.read_raw_log(path_to_bot_log)
        return "SUCCESS"

    elif command_type == Authorized.AUTH.value:
        bot.sendMessage(chat_id, "Reading raw log file...")
        raw_log = Log.read_raw_log(path_to_log)
        return "SUCCESS"

    elif command_type == Authorized.STATS.value:
        bot.sendMessage(chat_id, "Reading log file...")
        file_data = ""

        for line in Log.mine_log_task(path_to_log, users):
            file_data += "{}\n".format(line)

            if len(file_data) > MAX_LENGTH_OF_MESSAGE:
                bot.sendMessage(chat_id, file_data)
                file_data = ""

        bot.sendMessage(chat_id, file_data)
        print(file_data)

        return "SUCCESS"

    elif command_type == Authorized.STATS_TIME.value:
        hours_format = re.compile(time_pattern)
        if not hours_format.match(command_mode):
            bot.sendMessage(chat_id, "Incorrect pattern for time. Expected HH:mm but got: '{}'".format(command_mode))
            return "FAILED "

        schedule.every().day.at(command_mode).do(Log.mine_log_task, chat_id).tag(chat_id)

        bot.sendMessage(chat_id, "Notification has been set everyday at: {}.".format(command_mode))
        bot.sendMessage(chat_id, "Remember that, set time before 23:49.")
        return "SUCCESS"

    elif command_type == Authorized.STATS_JOBS.value:
        bot.sendMessage(chat_id, "Function for notification: Log.mine_log_task(CHAT_ID)")
        bot.sendMessage(chat_id, "All daily task are listed down:\n{}".format(schedule.get_jobs()))
        return "SUCCESS"

    elif command_type == Authorized.STATS_CANCEL.value:
        schedule.clear(chat_id)
        bot.sendMessage(chat_id, "Log notification has been canceled for chat id: {}".format(chat_id))
        return "SUCCESS"

    else:
        return normal_commands(user_id, chat_id, command_type)


def normal_commands(user_id, chat_id, command_type):
    if command_type == Unauthorized.ROLL.value:
        bot.sendMessage(chat_id, random.randint(1, 6))
        return "SUCCESS"

    elif command_type == Unauthorized.TIME.value:
        bot.sendMessage(chat_id, str(datetime.datetime.now()))
        return "SUCCESS"

    elif command_type == Unauthorized.ID.value:
        bot.sendMessage(chat_id, "Your telegram id is: {}".format(user_id))
        return "SUCCESS"

    else:
        bot.sendMessage(chat_id, "Sorry, unsupported command: {} ;//".format(command_type))
        return "FAILED "


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
        status = owners_commands(user_id, chat_id, command_type, command_mode)

    else:
        status = normal_commands(user_id, chat_id, command_type)

    print(' {},       {},      {},     {},     {} '
          .format(datetime.date.today(), chat_id, user_id, status, command))


MessageLoop(bot, handle).run_as_thread()
# ################# DO NOT DELETE THIS LINE #################
# redirect_std_out()
print("I am listening since {}...".format(datetime.date.today()))
print('     Date,           User,          Chat id,      Status,     Command')
while 1:
    schedule.run_pending()
    time.sleep(100)
