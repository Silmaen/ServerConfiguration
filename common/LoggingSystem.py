"""
all logging functions here
"""
from common.AllDefaultParameters import *
from common.databasehelper import DatabaseHelper
import datetime

db_helper = DatabaseHelper()
message_level_decorator = ["ERROR ", "WARNING ", "MESSAGE ", "DEBUG "]


class ErrorData:
    """
    class to exchange error data with the database
    """
    def __init__(self, who: str = "", message: str = "", time: datetime.datetime = datetime.datetime.now(), _id: int = 0):
        self.who = who
        self.message = message
        self.time = time
        self.ID = _id

    def __str__(self):
        if self.who != "":
            return self.time.strftime("%Y %h %d %H:%M:%S") + " [" + self.who + "] : " + message_level_decorator[0] + \
                   self.message
        else:
            return self.time.strftime("%Y %h %d %H:%M:%S") + " [robot] : " + self.message

    def __lt__(self, other):
        return self.time < other.time

    def to_dict(self, with_id: bool = False):
        """
        get a dict gathering attributes of this class (mainly for database interaction)
        :param with_id: if the ID should be included in the dict
        :return:
        """
        if with_id:
            return {"ID": self.ID, "who": self.who, "message": self.message, "time": self.time}
        else:
            return {"who": self.who, "message": self.message, "time": self.time}

    def to_md_array(self):
        """
        return an array item with md format
        :return:
        """
        return [self.time.strftime("*%Y-%h-%d %H:%M:%S*"), "**" + self.who + "**", self.message]

    def from_dict(self, content: dict):
        """
        update informations based of the content of the dict
        :param content: dict with informations
        """
        if "ID" in content:
            self.ID = content.get("ID")
        if "who" in content:
            self.who = content.get("who")
        if "message" in content:
            self.message = content.get("message")
        if "time" in content:
            self.time = content.get("time")

    def add_to_database(self):
        """
        add this error to the database if not already exists
        :return: False if the insertion fails
        """
        return db_helper.insert("ErrorList", self.to_dict())

    def get_db_id(self):
        """
        return the data id of this item (the last one in case of duplication, or -1 if not exists
        :return: the id of
        """
        return db_helper.getId("ErrorList", self.to_dict())


class Logger:
    """
    class used to log messages (singleton design pattern)
    """
    def __init__(self, destination=None, level: int = -1):
        import os
        log_data = os.path.join(data_dir, "log_info.dat")
        self.destination = None
        self.level = -1
        self.isfile = False
        if not destination and level < 0:
            if not os.path.exists(log_data):
                print("No default value for logging")
                return
            else:
                fd = open(log_data)
                lines = fd.readlines()
                fd.close()
                for line in lines:
                    if len(line.strip()) == 0 or line.strip().startswith("#"):
                        continue
                    if not self.destination:
                        self.destination = line.strip()
                        continue
                    try:
                        self.level = int(line)
                    except:
                        self.level = -1
                    break
                if self.level < 0:
                    print("Badly-formed datafile for logging")
                    return
        else:
            self.destination = destination
            self.level = min(max(0, level), len(message_level_decorator))
            fd = open(log_data, "w")
            fd.write(self.destination + "\n")
            fd.write(str(self.level) + "\n")
            fd.close()
        self.isfile = self.destination.lower() != "console"

    def __str__(self):
        return repr(self) + str(self.level) + " " + str(self.destination)

    def new_log(self):
        """
        start the log in a new file
        """
        import time
        if self.isfile:
            f = open(self.destination, "w")
            f.write(time.strftime("%Y %h %d %H:%M:%S") + " [log] : Starting new log file\n")
            f.close()
        else:
            pass  # nothing to do here

    def log(self, who: str, message: str, level: int = 2):
        """
        log the message to the destination
        :param message: the message to log as a string
        :param who: the sender of the message
        :param level: the level of the message (level higher than the defined one will not be printed)
        """
        import time
        level = min(abs(level), len(message_level_decorator))
        if who == "" or level > self.level:
            return
        to_print = time.strftime("%Y %h %d %H:%M:%S") + " [" + who + "] : " + message_level_decorator[level] + message
        if self.isfile:
            if not os.path.exists(self.destination):
                self.new_log()
            f = open(self.destination, "a")
            f.write(to_print + "\n")
            f.close()
        else:
            print(to_print)

    def log_error(self, who: str, message: str):
        """
        log a error
        it will print into the log file as will do the log function bur also will add an entry in the error data base
        :param who: sender of the error
        :param message: the error message
        """
        self.log(who, message, 0)
        if is_system_production():
            error = ErrorData(who, message)
            error.add_to_database()


def get_error_list(start_time: datetime.datetime = datetime.datetime.now(),
                   end_time: datetime.datetime = datetime.datetime.now()):
    """
    get a list of error between 2 dates
    :param start_time: lower date
    :param end_time: higher date
    :return: list of error
    """
    true_end_time = max(start_time, end_time)
    true_start_time = min(start_time, end_time)
    if true_end_time - true_start_time < datetime.timedelta(seconds = 1):
        true_end_time = true_start_time
        true_start_time = true_end_time - datetime.timedelta(days = 1)
    ret, content = db_helper.select("ErrorList", "WHERE `time` BETWEEN '" + str(true_start_time) + "' AND '" + str(true_end_time) + "'")
    if not ret:
        return []
    ret = []
    for cc in content:
        err = ErrorData()
        err.from_dict(cc)
        ret.append(err)
    return ret
