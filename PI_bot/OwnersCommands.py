from enum import Enum
from PrimitiveLogger import Log
from PrimitiveLogger import LogSender
import re
import schedule
import PublicCommands

time_pattern = "^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"


def process_daily_log(chat_id, bot, max_mess_len, path_to_log, users):
    statistics_log = Log.mine_log_task(path_to_log, users)
    LogSender.send_log(statistics_log, chat_id, bot, max_mess_len)


class AuthorizedCommands(Enum):
    SELF = '/self'
    AUTH = '/auth'
    STATS = '/stats'
    STATS_TIME = '/stats_time'
    STATS_JOBS = '/stats_jobs'
    STATS_CANCEL = '/stats_cancel'


class Admin:

    def __init__(self, path_to_bot_log, path_to_log, max_mess_len, users):
        self.path_to_bot_log = path_to_bot_log
        self.path_to_log = path_to_log
        self.MAX_LENGTH_OF_MESSAGE = max_mess_len
        self.users = users

    def process_command(self, user_id, chat_id, bot, command_type, command_mode):
        if command_type == AuthorizedCommands.SELF.value:

            bot.sendMessage(chat_id, "Reading raw log file...")
            raw_log = Log.read_raw_log(self.path_to_bot_log)
            LogSender.send_log(raw_log, chat_id, bot, self.MAX_LENGTH_OF_MESSAGE)

            return "SUCCESS"

        elif command_type == AuthorizedCommands.AUTH.value:

            bot.sendMessage(chat_id, "Reading raw log file...")
            raw_log = Log.read_raw_log(self.path_to_log)
            LogSender.send_log(raw_log, chat_id, bot, self.MAX_LENGTH_OF_MESSAGE)

            return "SUCCESS"

        elif command_type == AuthorizedCommands.STATS.value:

            bot.sendMessage(chat_id, "Reading log file...")
            statistics_log = Log.mine_log_task(self.path_to_log, self.users)
            LogSender.send_log(statistics_log, chat_id, bot, self.MAX_LENGTH_OF_MESSAGE)

            return "SUCCESS"

        elif command_type == AuthorizedCommands.STATS_TIME.value:
            hours_format = re.compile(time_pattern)
            if not hours_format.match(command_mode):
                bot.sendMessage(chat_id,
                                "Incorrect pattern for time. Expected HH:mm but got: '{}'".format(command_mode))
                return "FAILED "

            schedule.every().day.at(command_mode).do(process_daily_log, chat_id, bot, self.MAX_LENGTH_OF_MESSAGE, self.path_to_log, self.users).tag(chat_id)

            bot.sendMessage(chat_id, "Notification has been set everyday at: {}.".format(command_mode))
            bot.sendMessage(chat_id, "Remember that, set time before 23:49.")
            return "SUCCESS"

        elif command_type == AuthorizedCommands.STATS_JOBS.value:
            bot.sendMessage(chat_id, "Function for notification: Log.mine_log_task(CHAT_ID)")
            bot.sendMessage(chat_id, "All daily task are listed down:\n{}".format(schedule.get_jobs()))
            return "SUCCESS"

        elif command_type == AuthorizedCommands.STATS_CANCEL.value:
            schedule.clear(chat_id)
            bot.sendMessage(chat_id, "Log notification has been canceled for chat id: {}".format(chat_id))
            return "SUCCESS"

        else:
            return PublicCommands.public_commands(user_id, chat_id, bot, command_type)
