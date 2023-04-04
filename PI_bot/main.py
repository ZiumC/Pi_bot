import random
import sys
import os
import time
import datetime
import schedule
import re
import telepot
from telepot.loop import MessageLoop

OWNERS_ID = []
bot = telepot.Bot('')

time_pattern = "^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
path_to_bot_log = ""
unauthorized_supported_commands = ['/roll',
                                   '/time',
                                   '/id']

authorized_supported_commands = ['/self',
                                 '/auth',
                                 '/stats',
                                 '/stats_time',
                                 '/stats_jobs',
                                 '/stats_cancel']

combined_commands = [authorized_supported_commands,
                     unauthorized_supported_commands]


def verify_command(command):
    if combined_commands[0].__contains__(command):
        return True
    elif combined_commands[1].__contains__(command):
        return True
    else:
        return False


def redirect_std_out():
    path = ''
    sys.stdout.flush()
    os.system(path)


def mine_log_task(chat_id):
    bot.sendMessage(chat_id, "TEST")
    return


def owners_commands(user_id, chat_id, command_type, command_mode):
    if OWNERS_ID.__contains__(user_id):
        if command_type == authorized_supported_commands[0]:
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

        elif command_type == authorized_supported_commands[1]:
            bot.sendMessage(chat_id, "/auth appears soon")
            return "SUCCESS"

        elif command_type == authorized_supported_commands[2]:
            bot.sendMessage(chat_id, "/stats appears soon")
            return "SUCCESS"

        elif command_type == authorized_supported_commands[3]:
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
        elif command_type == authorized_supported_commands[4]:
            bot.sendMessage(chat_id, "All daily task are listed down:\n{}"
                            .format(schedule.get_jobs()))
            return "SUCCESS"

        elif command_type == authorized_supported_commands[5]:
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


def handle(msg):
    global status
    chat_id = msg['chat']['id']
    command = msg['text']
    user_id = msg['from']['id']

    split_command = command.split(" ")
    command_type = split_command[0]
    command_mode = ""

    if len(split_command) > 1:
        command_mode = split_command[1]

    if not verify_command(command_type):
        bot.sendMessage(chat_id, "Sorry, unsupported command: {} ;//".format(command_type))
        status = "FAILED "

    else:
        if command_type == unauthorized_supported_commands[0]:
            bot.sendMessage(chat_id, random.randint(1, 6))
            status = "SUCCESS"

        elif command_type == unauthorized_supported_commands[1]:
            bot.sendMessage(chat_id, str(datetime.datetime.now()))
            status = "SUCCESS"

        elif command_type == unauthorized_supported_commands[2]:
            bot.sendMessage(chat_id, "Your telegram id is: {}".format(user_id))
            status = "SUCCESS"

        else:
            status = owners_commands(user_id, chat_id, command_type, command_mode)

    print('{}   User: {}    |    Chat id: {}  |   Command status: {}    |   User input command: {}'
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

while 1:
    schedule.run_pending()
    time.sleep(100)
