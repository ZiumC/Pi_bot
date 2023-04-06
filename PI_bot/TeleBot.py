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


class Log:
    # processing date from first fragment of log
    @staticmethod
    def get_date(date_line):
        return date_line.replace(" pi ", "")

    # processing ip data from second fragment of log
    @staticmethod
    def get_ip(ip_data_line):
        ip_with_port_fragment = ip_data_line.split(" from ")[1]
        ip_data = ip_with_port_fragment.split(" port ")
        return "{}:{}".format(ip_data[0], ip_data[1])

    @staticmethod
    def send_log(message_to_sent, chat_id):
        buffered_string = ""

        for line_to_build in message_to_sent:
            buffered_string += "{}\n".format(line_to_build)

            # 3800 is needed to check because max length bot message is 4096 so 3800 is quite safe
            if len(buffered_string) > MAX_LENGTH_OF_MESSAGE:
                bot.sendMessage(chat_id, buffered_string)
                buffered_string = ""
        bot.sendMessage(chat_id, buffered_string)
        buffered_string = ""

    @staticmethod
    def mine_log_task(chat_id):
        file_sshd_service_data = []
        build_message = []
        # reading log here
        with open(path_to_log, encoding='utf8') as f:
            for line in f:
                if 'sshd' in line:
                    file_sshd_service_data.append("{}".format(line.strip()))

        # mining text for each defined user
        for user in users:
            for line_file in file_sshd_service_data:

                # splitting by "sshd" is required, because it allows to
                # process independently date fragment and user, ip address, port fragment
                split_line = line_file.split("sshd")

                # processing fragment with user, ip address, port
                if user in split_line[1]:

                    # login correct
                    if 'Accepted' in line_file:
                        string_log = " - {} | {}".format(Log.get_date(split_line[0]), Log.get_ip(split_line[1]))
                        users_correct_logins_in[user].append(string_log)

                    # login failed
                    elif 'Failed' in line_file:
                        string_log = " - {} | {}".format(Log.get_date(split_line[0]), Log.get_ip(split_line[1]))
                        users_failed_logins_tries[user].append(string_log)

                # not existing user in SFTP server
                elif 'Invalid' in line_file:
                    string_log = " - {} | {}".format(Log.get_date(split_line[0]), split_line[1].split(":")[1])
                    other_invalid_tries.append(string_log)

            correct_count = 0
            failed_count = 0
            build_message.append("[{}] Log for user: {} ".format(datetime.date.today(), user))
            build_message.append("Total correct logins")

            # building correct log for user
            for user_correct_log in users_correct_logins_in[user]:
                correct_count += 1
                build_message.append(user_correct_log)
            if correct_count == 0:
                build_message.append(" - no correct logins for user: {}".format(user))

            # building incorrect log for user
            build_message.append("Total failed logins")
            for user_failed_log in users_failed_logins_tries[user]:
                failed_count += 1
                build_message.append(user_failed_log)
            if failed_count == 0:
                build_message.append(" - no failed logins for user: {}".format(user))

            users_correct_logins_in[user].clear()
            users_failed_logins_tries[user].clear()
            # building summary
            build_message.append(
                "Correct logins count: {}, Failed logins count: {}\n".format(correct_count, failed_count))

        # building invalid log
        build_message.append("\nInvalid logins to SFTP server")
        if len(other_invalid_tries) == 0:
            build_message.append(" - no invalid logins to server")
        else:
            for invalid_log in other_invalid_tries:
                build_message.append(invalid_log)

        # sending message to user
        Log.send_log(build_message, chat_id)
        file_sshd_service_data.clear()
        build_message.clear()
        other_invalid_tries.clear()

    @staticmethod
    def read_raw_log(chat_id, path):
        file_data = ""
        with open(path, encoding='utf8') as f:
            for line in f:
                file_data += line.strip()
                if len(file_data) > MAX_LENGTH_OF_MESSAGE:
                    bot.sendMessage(chat_id, "{}\n".format(file_data))
                    file_data = ""

        bot.sendMessage(chat_id, file_data)


def owners_commands(user_id, chat_id, command_type, command_mode):
    if command_type == Authorized.SELF.value:
        bot.sendMessage(chat_id, "Reading raw log file...")
        Log.read_raw_log(chat_id, path_to_bot_log)
        return "SUCCESS"

    elif command_type == Authorized.AUTH.value:
        bot.sendMessage(chat_id, "Reading raw log file...")
        Log.read_raw_log(chat_id, path_to_log)
        return "SUCCESS"

    elif command_type == Authorized.STATS.value:
        bot.sendMessage(chat_id, "Reading log file...")
        Log.mine_log_task(chat_id)
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
