"""
Description of class to time some cone
"""


class CodeTimer:
    """
    simple chorno to start/stop/reset
    """
    def __init__(self, name = ""):
        import time
        self.name = name
        self.start = time.time()
        self.long = 0
        self.__started = True

    def stop(self):
        """
        stop the chrono, and add the curent time to total long
        """
        import time
        if self.__started:
            self.long += time.time() - self.start
        self.__started = False

    def start(self):
        """
        setup start time to now and set chrono running
        """
        import time
        if not self.__started:
            self.start = time.time()
        self.__started = True

    def reset(self):
        """
         reset total long to zero then start
        """
        import time
        self.long = 0
        self.start = time.time()
        self.__started = True

    def get_long(self):
        """
        get the total chronometer value
        :return: long if the chrono is stopped, long plus current chrono else
        """
        import time
        if self.__started:
            return self.long + time.time() - self.start
        else:
            return self.long

    def format_long(self, name: str = ""):
        """
        format a string of long with units
        :return: long displayed with unit
        """
        if name not in ["", None]:
            self.name = name
        return self.name + " {:.6f} s".format(self.get_long())

    def format_current(self, name: str = ""):
        """
        format a string of current timer with units
        :return: long displayed with unit
        """
        import time
        return name + " {:.6f} s".format(time.time() - self.start)
