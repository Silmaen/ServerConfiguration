"""
definition of Database helper class
"""
from .maintenance import *
import MySQLdb

MySQLParams = {
    'host': "localhost",
    'user': "robot",
    'passwd': "Robot123",
    'db': "adiministration"
}


class DatabaseHelper:
    """
    class to handle database and communication with it
    """
    def __init__(self):
        self.__con = None
        self.__cur = None
        self.__error_code = 0

    def __connect(self):
        try:
            self.__con = MySQLdb.connect(**MySQLParams)
        except MySQLdb.Error as e:
            logger.log("DatabaseHelper", "MySQLdb Error " + str(e.args[0]) + ": " + str(e.args[1]))
            self.__con = None
            self.__error_code = 1
            return
        except:
            logger.log("DatabaseHelper", "Unknown Error during connexion!")
            self.__con = None
            self.__error_code = 2
            return
        if not self.__con:
            logger.log("DatabaseHelper", "Connexion Error")
            self.__error_code = 3
            return
        self.__cur = self.__con.cursor()
        self.__error_code = 0

    def __close_connection(self):
        """
        simply close active connection and clear error code
        """
        if self.__con:
            self.__con.close()
        self.__cur = None
        self.__error_code = 0

    def __request(self, request):
        if not self.__con:
            self.__connect()
            if self.__error_code != 0:
                return False
        try:
            self.__cur.execute(request)
            self.__con.commit()
        except MySQLdb.Error as e:
            logger.log("DatabaseHelper", "MySQLdb Error " + str(e.args[0]) + ": " + str(e.args[1]))
            self.__close_connection()
            return False
        except:
            logger.log("DatabaseHelper", "Unknown Error for querry: '" + str(request) + "'")
            self.__close_connection()
            return False
        return True

    def select(self, tablename: str, filters: str = ""):
        """
        do a select request to the database
        :param tablename: the table to use
        :param filters: additional parameters to the request
        :return: (request succes, list of row as dictionaries)
        """
        if tablename == "":
            logger.log("DatabaseHelper", "malformed select request, unable to get table name")
            return False, []
        # get column name
        req = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'" + tablename + "'"
        ret = self.__request(req)
        if not ret:
            logger.log("DatabaseHelper", "Unable to get column names")
            return False, []
        col_names = [r[0] for r in self.__cur.fetchall()]
        req = "SELECT * FROM `" + tablename + "`"
        if filters != "":
            req += " " + filters
        ret = self.__request(req)
        if not ret:
            logger.log("DatabaseHelper", "request error: '" + req + "'")
            return False, []
        return True, [dict(zip(col_names, r)) for r in self.__cur.fetchall()]
