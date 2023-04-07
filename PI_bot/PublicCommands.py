from enum import Enum
import random
import datetime


class Unauthorized(Enum):
    ROLL = '/roll'
    TIME = '/time'
    ID = '/id'


def public_commands(user_id, chat_id, bot, command_type):
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
