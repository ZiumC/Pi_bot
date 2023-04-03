import time
import random
import datetime
import telepot
import sys
import os
from telepot.loop import MessageLoop

OWNERS_ID = []
bot = telepot.Bot('')

unauthorized_supported_commands = ['/roll',
                                   '/time',
                                   '/my-id',
                                   '/ai']

authorized_supported_commands = ['/self-log',
                                 '/auth-log',
                                 '/stats']

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


def owners_commands(user_id, chat_id, command):
    if OWNERS_ID.__contains__(user_id):
        if command == authorized_supported_commands[0]:
            bot.sendMessage(chat_id, "/self-log appears soon")
        elif command == authorized_supported_commands[1]:
            bot.sendMessage(chat_id, "/auth-log appears soon")
        elif command == authorized_supported_commands[2]:
            bot.sendMessage(chat_id, "/stats appears soon")
    else:
        bot.sendMessage(chat_id, "Sorry, you are unauthorized to use that command!")


def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    user_id = msg['from']['id']

    print('{}   User: {}    |    Chat id: {}  |   User input command: {}'
          .format(datetime.datetime.now(),
                  chat_id,
                  user_id,
                  command))

    if not verify_command(command):
        bot.sendMessage(chat_id, "Sorry, unsupported command: {} ;//".format(command))

    else:
        if command == unauthorized_supported_commands[0]:
            bot.sendMessage(chat_id, random.randint(1, 6))

        elif command == unauthorized_supported_commands[1]:
            bot.sendMessage(chat_id, str(datetime.datetime.now()))

        elif command == unauthorized_supported_commands[2]:
            bot.sendMessage(chat_id, "Your telegram id is: {}".format(msg['from']['id']))

        elif command == unauthorized_supported_commands[3]:
            bot.sendMessage(chat_id, "/ai feature will appear soon...")

        else:
            owners_commands(user_id, chat_id, command)


MessageLoop(bot, handle).run_as_thread()
# ################# DO NOT DELETE THIS LINE #################
# redirect_std_out()
print("I am listening since {}...".format(datetime.datetime.now()))

while 1:
    time.sleep(10)
