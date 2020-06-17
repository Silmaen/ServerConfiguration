"""
script to test the database
"""
import unittest
from common.databasehelper import DatabaseHelper
from common.maintenance import is_system_production, logger


class TestingDatabase(unittest.TestCase):
    """
    unit test relatives to the database helper
    """
    def test_connexion(self):
        """
        basic test to read connected machines
        """
        db = DatabaseHelper()
        if is_system_production():
            good, results = db.select('ActiveMachine')
            self.assertTrue(good)
            self.assertTrue(len(results) > 0)
        else:
            logger.log("TestingDatabase", "Warning: connexion not tested, because not in production", 1)
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
