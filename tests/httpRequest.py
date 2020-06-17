"""
testing http requests
"""
import unittest
from common.httputils import exist_http_page


class MyTestCase(unittest.TestCase):
    def test_page_exists(self):
        self.assertTrue(exist_http_page("https://www.argawaen.net"))
        self.assertTrue(exist_http_page("http://www.google.fr"))
        self.assertFalse(exist_http_page("https://www.argawaen.net/pagequinexistepas"))
        self.assertFalse(exist_http_page("https://www.sitequinexistepas.net/"))


if __name__ == '__main__':
    unittest.main()
