# Pi_bot
This application has been written in Python 3.9 to work with telegram API.

# Instalation
1. To run this application just dowloand latest zip file <a href="https://github.com/ZiumC/Pi_bot/releases/tag/v1.0" rel="nofollow">this link</a>.
2. Extract files, then open main folder ```Pi_bot-1.0/Pi_bot-1.0/PI_bot``` in InteliJ.
3. You have to install Python plugin for InteliJ.
4. Next you should define Python interpreter for project (if you have installed already version 3.9 just use it).
5. You have to install the following packages:
   a. schedule
   b. telepot
6. Fill up empty fields (that i'll explain in '_Filling up empty fields_' section) and run class ```TeleBot.py```

# Filling up empty fields
``` python
# your telegram ID
OWNERS_ID = []
# your telegram bot API KEY
bot = telepot.Bot('')

# telegram bot can handle with 4096 message length
# i recommend that to leave this value at 3800
MAX_LENGTH_OF_MESSAGE = 3800


# specify output path for log here
path_to_bot_log = ""

# if you want to mine your file auth.log just put path here.
# On Linux is usually: /var/log/auth.log
path_to_log = ""

# put here your name which you are using in SFTP
users = ['pi']
```

# Features
1. This bot allows to use public commands and administrative commands.
2. This app allows to log every single triggered action that user has made.
3. You can set task that bot will send you information daily about ```auth.log``` file.

# Administrative commands (OwnersCommands.py)
1. ```/self``` - sends bot log
2. ```/auth``` - sends raw content of file ```auth.log```
3. ```/stats``` - reads content of ```auth.log``` file, then formats and sends message about who has logged into server, from which IP address for each defined user. Also sends info about failed login attempts.
4. ```/mount``` - (experimental) command should run script for mounting disc on linux. To use this you have go to file ```OwnersCommands.py``` and edit line no. 85 ```subprocess.call(['sh', '[PATH TO YOUR SCRIPT]'])``` and paste path to your script file.
5. ```/stats_time``` - this command sends to user formatted data like command ```/starts``` but it also accepts parameter (time) onn what time bot will send notification to user.
6. ```/stats_jobs``` - sends list of all active jobs.
7. ```/stats_cancel``` - cancels daily notification.

# Public commands (PublicCommands.py)
1. ```/roll``` - rolls digit in range 1-6
2. ```/time``` - sends current time of machine that hosts bot
3. ```/id``` - sends to user telegram account ID

# Documents
1. How to create a <a href="https://core.telegram.org/bots/tutorial#getting-ready" rel="nofollow">telegram bot with BotFather</a>.
