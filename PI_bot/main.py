import random
import sys
import os
import time
import datetime
import schedule
import re
import telepot
from enum import Enum
from telepot.loop import MessageLoop

OWNERS_ID = []
bot = telepot.Bot('')

time_pattern = "^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
path_to_bot_log = ""
output_path = ""


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


# unauthorized_supported_commands = ['/roll',
#                                    '/time',
#                                    '/id']

# authorized_supported_commands = ['/self',
#                                  '/auth',
#                                  '/stats',
#                                  '/stats_time',
#                                  '/stats_jobs',
#                                  '/stats_cancel']

# combined_commands = [authorized_supported_commands,
#                      unauthorized_supported_commands]


# def verify_command(command):
# if combined_commands[0].__contains__(command):
#     return True
# elif combined_commands[1].__contains__(command):
#     return True
# else:
#     return False


def redirect_std_out():
    sys.stdout.flush()
    os.system(output_path)


def mine_log_task(chat_id):
    bot.sendMessage(chat_id, "TEST")
    return


def owners_commands(user_id, chat_id, command_type, command_mode):
    if OWNERS_ID.__contains__(user_id):
        if command_type == Authorized.SELF:
            file_data = ""
            bot.sendMessage(chat_id, "Reading file...")
            with open(path_to_bot_log, encoding='utf8') as f:
                for line in f:
                    file_data += line.strip()
                    if len(file_data) > 4080:
                        bot.sendMessage(chat_id, "{}\n".format(file_data))
                        file_data = ""

            bot.sendMessage(chat_id, file_data)
            return "SUCCESS"

        elif command_type == Authorized.AUTH:
            bot.sendMessage(chat_id, "/auth appears soon")
            return "SUCCESS"

        elif command_type == Authorized.STATS:
            bot.sendMessage(chat_id, "/stats appears soon")
            return "SUCCESS"

        elif command_type == Authorized.STATS_TIME:
            hours_format = re.compile(time_pattern)
            if not hours_format.match(command_mode):
                bot.sendMessage(chat_id, "Incorrect pattern for time. Expected HH:mm but got: '{}'"
                                .format(command_mode))
                return "FAILED "

            schedule.every().day.at(command_mode).do(mine_log_task, chat_id).tag(chat_id)
            bot.sendMessage(chat_id, "Log notification has been set for chat id: {} everyday at: {}."
                            .format(chat_id, command_mode))
            bot.sendMessage(chat_id, "Remember that, set time before 23:49.")
            return "SUCCESS"
        elif command_type == Authorized.STATS_JOBS:
            bot.sendMessage(chat_id, "All daily task are listed down:\n{}"
                            .format(schedule.get_jobs()))
            return "SUCCESS"

        elif command_type == Authorized.STATS_CANCEL:
            schedule.clear(chat_id)
            bot.sendMessage(chat_id, "Log notification has been canceled for chat id: {}"
                            .format(chat_id))
            return "SUCCESS"

        else:
            bot.sendMessage(chat_id, "Super user, unsupported command: {} ;//"
                            .format(command_type))
            return "FAILED "
    else:
        bot.sendMessage(chat_id, "Sorry, you are unauthorized to use that command!")
        return "FAILED "


def normal_commands(user_id, chat_id, command_type):
    if command_type == Unauthorized.ROLL:
        bot.sendMessage(chat_id, random.randint(1, 6))
        return "SUCCESS"

    elif command_type == Unauthorized.TIME:
        bot.sendMessage(chat_id, str(datetime.datetime.now()))
        return "SUCCESS"

    elif command_type == Unauthorized.ID:
        bot.sendMessage(chat_id, "Your telegram id is: {}".format(user_id))
        return "SUCCESS"

    else:
        bot.sendMessage(chat_id, "Sorry, unsupported command: {} ;//".format(command_type))
        return "FAILED "


def handle(msg):
    global status
    chat_id = msg['chat']['id']
    command = msg['text']
    user_id = msg['from']['id']

    split_command = command.split(" ")
    command_type = split_command[0]
    command_mode = ""

    if OWNERS_ID.__contains__(user_id):
        if len(split_command) > 1:
            command_mode = split_command[1]
        status = owners_commands(user_id, chat_id, command_type, command_mode)

    else:
        status = normal_commands(user_id, chat_id, command_type)

    print(' {},       {},      {},     {},     {} '
          .format(datetime.datetime.now(),
                  chat_id,
                  user_id,
                  status,
                  command))


status = "FAILED "
MessageLoop(bot, handle).run_as_thread()
# ################# DO NOT DELETE THIS LINE #################
# redirect_std_out()
print("I am listening since {}...".format(datetime.datetime.now()))
print(' Date,       User,      Chat id,     Status,     Command ')

while 1:
    schedule.run_pending()
    time.sleep(100)
