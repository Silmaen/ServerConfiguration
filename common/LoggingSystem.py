"""
all logging functions here
"""
from common.AllDefaultParameters import *


class Logger:
    """
    calls used to log messages (singleton design pattern)
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
            self.level = level
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

    def log(self, message: str, who: str = "", level: int = 1):
        """
        log the message to the destination
        :param message: the message to log as a string
        :param who: the sender of the message
        :param level: the level of the message ( level higher than  the defined one will not be printed)
        """
        import time
        if who == "" or abs(level) > self.level:
            return
        if self.isfile:
            if not os.path.exists(self.destination):
                self.new_log()
            f = open(self.destination, "a")
            f.write(time.strftime("%Y %h %d %H:%M:%S") + " [" + who + "] : " + message + "\n")
            f.close()
        else:
            print(time.strftime("%Y %h %d %H:%M:%S") + " [" + who + "] : " + message)

