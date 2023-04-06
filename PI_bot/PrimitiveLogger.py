import datetime


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
    def send_log(message_to_sent, chat_id, bot, max_mess_len=3800):
        buffered_string = ""

        for line_to_build in message_to_sent:
            buffered_string += "{}\n".format(line_to_build)

            # 3800 is needed to check because max length bot message is 4096 so 3800 is quite safe
            if len(buffered_string) > max_mess_len:
                bot.sendMessage(chat_id, buffered_string)
                buffered_string = ""
        bot.sendMessage(chat_id, buffered_string)

    @staticmethod
    def read_raw_log(path):
        file_data = []

        with open(path, encoding='utf8') as f:
            for line in f:
                file_data.append(line.strip())

        return file_data

    @staticmethod
    def mine_log_task(path_to_log, user_list):
        file_sshd_service_data = []

        users_correct_logins_in = []
        users_failed_logins_tries = []
        other_invalid_tries = []

        build_message = []

        # reading log here
        with open(path_to_log, encoding='utf8') as f:
            for line in f:
                if 'sshd' in line:
                    file_sshd_service_data.append("{}".format(line.strip()))

        # mining text for each defined user
        for user in user_list:
            for line_file in file_sshd_service_data:

                # splitting by "sshd" is required, because it allows to
                # process independently date fragment and user, ip address, port fragment
                split_line = line_file.split("sshd")

                # processing fragment with user, ip address, port
                if user in split_line[1]:

                    # login correct
                    if 'Accepted' in line_file:
                        string_log = " - {} | {}".format(Log.get_date(split_line[0]),
                                                         Log.get_ip(split_line[1]))
                        users_correct_logins_in.append(string_log)

                    # login failed
                    elif 'Failed' in line_file:
                        string_log = " - {} | {}".format(Log.get_date(split_line[0]),
                                                         Log.get_ip(split_line[1]))
                        users_failed_logins_tries.append(string_log)

                # not existing user in SFTP server
                elif 'Invalid' in line_file:
                    string_log = " - {} | {}".format(Log.get_date(split_line[0]), split_line[1].split(":")[1])
                    other_invalid_tries.append(string_log)

            build_message.append("[{}] Log for user: {} ".format(datetime.date.today(), user))

            correct_count = len(users_correct_logins_in)
            failed_count = len(users_failed_logins_tries)

            # building correct log for user
            build_message.append("Total correct logins")
            if correct_count == 0:
                build_message.append(" - no correct logins for user: {}".format(user))
            else:
                for user_correct_log in users_correct_logins_in:
                    build_message.append(user_correct_log)

            # building incorrect log for user
            build_message.append("Total failed logins")
            if failed_count == 0:
                build_message.append(" - no failed logins for user: {}".format(user))
            else:
                for user_failed_log in users_failed_logins_tries:
                    build_message.append(user_failed_log)

            users_correct_logins_in.clear()
            users_failed_logins_tries.clear()

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

        return build_message
