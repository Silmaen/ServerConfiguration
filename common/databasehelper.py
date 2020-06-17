"""
definition of Database helper class
"""
from common.AllDefaultParameters import *
import MySQLdb

if is_system_production():
    MySQLParams = {
        'host': "localhost",
        'user': "robot",
        'passwd': "Robot123",
        'db': "administration"
    }
else:
    MySQLParams = {
        'host': "localhost",
        'user': "robot",
        'passwd': "Robot123",
        'db': "administration_test"
    }

Valid_Tables = [
    "ActiveMachine",     # the currently connected machines that are in the database
    "ErrorList",         # list of errors
    "ConnexionArchive",  # archive of connected machine
]


database_error_file = os.path.join(log_dir, "db_errors.log")


def log_error(message: str):
    """
    special error
    :param message:
    :return:
    """
    from datetime import datetime
    if not os.path.exists(os.path.dirname(database_error_file)):
        os.makedirs(os.path.dirname(database_error_file))
    if not os.path.exists(database_error_file):
        f = open(database_error_file, "w")
    else:
        f = open(database_error_file, "a")
    f.write(str(datetime.now()) + " DB ERROR: " + message + '\n')
    f.close()


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
        except MySQLdb.Error as err:
            log_error(str(err))
            self.__con = None
            self.__error_code = 1
            return
        except Exception as err:
            log_error(str(err))
            self.__con = None
            self.__error_code = 2
            return
        if not self.__con:
            log_error("Unknwon error during connexion")
            self.__error_code = 3
            return
        self.__cur = self.__con.cursor()
        self.__error_code = 0

    def __close_connection(self):
        """
        simply close active connection and clear error code
        """
        if self.__con:
            try:
                self.__con.close()
            except MySQLdb.Error as err:
                log_error(str(err))
        self.__cur = None
        self.__con = None
        self.__error_code = 0

    def __check_table_name(self, table_name: str):
        """
        check for a valid table name
        :param table_name: the name of the table
        :return: True if the table name is valid
        """
        if table_name in Valid_Tables:
            return True
        log_error("invalid table Name '" + table_name +
                   "' valid names are: [" + " ".join(Valid_Tables) + "]")
        self.__error_code = 4
        return False

    def __request(self, request):
        if not self.__con:
            self.__connect()
            if self.__error_code != 0:
                return False
        try:
            self.__cur.execute(request)
            self.__con.commit()
        except MySQLdb.Error as e:
            log_error("MySQLdb Error " + str(e.args[0]) + ": " + str(e.args[1]) + " request: " + request)
            self.__close_connection()
            return False
        except Exception as err:
            log_error("Unknown Error for querry: '" + str(request) + "': " + str(err))
            self.__close_connection()
            return False
        return True

    def __exists_item(self, table_name: str, item_id: int):
        if not self.__check_table_name(table_name):
            return False
        req = "SELECT * FROM `" + table_name + "` WHERE `ID` = " + str(item_id)
        ret = self.__request(req)
        if not ret:
            return False
        return len(self.__cur.fetchall()) != 0

    def __check_column(self, table_name: str, content: dict):
        col_names = self.get_column_names(table_name)
        if len(col_names) == 0:
            return False
        for n in content:
            if n not in col_names:
                log_error("Bad item for insert into " + table_name + " '" + n +
                           "' valid items are: [" + ",".join(col_names) + "]")
                return False
        return True

    def get_column_names(self, table_name: str):
        """
        return the names of the columns of a given table
        :param table_name: the name of the table
        :return: the list of column names
        """
        if not self.__check_table_name(table_name):
            return []
        # get column name
        req = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + table_name + \
              "' AND TABLE_SCHEMA = '" + MySQLParams["db"] + "'"
        ret = self.__request(req)
        if not ret:
            return []
        return [r[0] for r in self.__cur.fetchall()]

    def select(self, table_name: str, filters: str = ""):
        """
        do a select request to the database
        :param table_name: the table to use
        :param filters: additional parameters to the request
        :return: (request success, list of row as dictionaries)
        """
        # SELECT * FROM <table_name> [Filters]
        if not self.__check_table_name(table_name):
            return False, []
        col_names = self.get_column_names(table_name)
        if len(col_names) == 0:
            return False, []
        req = "SELECT * FROM `" + table_name + "`"
        if filters != "":
            req += " " + filters
        ret = self.__request(req)
        if not ret:
            return False, []
        return True, [dict(zip(col_names, r)) for r in self.__cur.fetchall()]

    def insert(self, table_name: str, content: dict, unique: bool = False):
        """
        insert a item into the database
        :param table_name: the name of the table
        :param content: the content to add
        :param unique: if True, insert only if not already exists
        :return: request success
        """
        # INSERT INTO <table_name> ( <content.keys()> ) VALUES ( content.values() )
        if not self.__check_table_name(table_name):
            return False
        if not self.__check_column(table_name, content):
            return False
        if unique and self.getId(table_name, content, False) > 0:
            return False
        req = "INSERT INTO `" + table_name + "` "
        req += "(" + ", ".join(["`" + str(s) + "`" for s in content.keys()]) + ")"
        req += " VALUES (" + ", ".join(["'" + str(content[s]) + "'" for s in content.keys()]) + ")"
        return self.__request(req)

    def modify(self, table_name: str, content: dict):
        """
        modify an entry in the Database
        :param table_name: the table to search for entry
        :param content: the modified content (could be partial)
        :return:
        """
        # UPDATE `table_name` SET `filters.keys()` = filters.values() WHERE `table_name`.`Id` = content['Id']
        if not self.__check_table_name(table_name):
            return False
        if not self.__check_column(table_name, content):
            return False
        if 'ID' not in content:
            log_error("Modifiy error: the ID of the item to modify is not set")
        if not self.__exists_item(table_name, content['ID']):
            log_error("Modifiy warning: item with ID " + str(content['ID']) + " does not exists ")
            return False
        req = "UPDATE `" + table_name + "` SET " + \
              ", ".join(["`" + key + "` = '" + str(val) + "'" for key, val in content.items()]) + \
              " WHERE `" + table_name + "`.`ID` = " + str(content["ID"])
        return self.__request(req)

    def delete(self, table_name: str, id_to_delete: int):
        """
        delete an item by ID
        :param table_name: the table in which to delete
        :param id_to_delete: the ID of the item
        :return:
        """
        # DELETE FROM `table_name` WHERE `table_name`.`ID` = id_to_delete
        if not self.__check_table_name(table_name):
            return False
        if not self.__exists_item(table_name, id_to_delete):
            log_error("Delete warning: item with ID " + str(id_to_delete) + " does not exists ")
            return False
        req = "DELETE FROM `" + table_name + "` WHERE `" + table_name + "`.`ID` = " + str(id_to_delete)
        return self.__request(req)

    def getId(self, table_name: str, know_content: dict, unique: bool = True):
        """
        retrieve id of an element
        :param table_name: the name of the table to search in
        :param know_content: all known informations
        :param unique:
        :return:
        """
        if not self.__check_table_name(table_name):
            return -1
        if not self.__check_column(table_name, know_content):
            return -1
        req = "SELECT `ID` FROM `" + table_name + "` WHERE " + \
              " AND ".join(["`" + k + "` = '" + str(v) + "'" for k, v in know_content.items()])
        ret = self.__request(req)
        if not ret:
            return -1
        fetch = [r[0] for r in self.__cur.fetchall()]
        if len(fetch) == 0:
            return -1
        if len(fetch) != 1 and unique:
            return -1
        return fetch[-1]
