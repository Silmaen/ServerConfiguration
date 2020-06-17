"""
testing http requests
"""
import unittest
from common.httputils import exist_http_page, get_http_page


class MyTestCase(unittest.TestCase):
    def test_page_exists(self):
        self.assertTrue(exist_http_page("https://www.argawaen.net"))
        self.assertTrue(exist_http_page("http://www.google.fr"))
        self.assertFalse(exist_http_page("https://www.argawaen.net/pagequinexistepas"))
        self.assertFalse(exist_http_page("https://www.sitequinexistepas.net/"))

    def test_page_get(self):
        lines = get_http_page("https://myexternalip.com/raw")
        self.assertTrue(len(lines) == 1)


if __name__ == '__main__':
    unittest.main()
