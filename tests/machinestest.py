"""
testing relative to the connected machines
"""
import unittest
from common.machine import Machine, mac_compare, str_is_ip
import datetime


class TestingSingleMachine(unittest.TestCase):
    def test_base(self):
        """
        Test the basic creation of a machine
        """
        mac = Machine("toto.argawaen.net", "00:00:00:00:00:00:00:00", "0.0.0.0", False,
                      datetime.datetime(2020, 1, 1, 6))
        self.assertEqual(mac.name, "toto.argawaen.net")
        self.assertEqual(mac.mac, "00:00:00:00:00:00:00:00")
        self.assertEqual(mac.ip, "0.0.0.0")
        self.assertFalse(mac.outmachine)
        self.assertFalse(mac.inDB)
        self.assertFalse(mac.inDNS)
        self.assertFalse(mac.inLease)
        self.assertFalse(mac.inDNStemplate)
        self.assertEqual(mac.get_short_name(), "toto")

    def test_timestamp(self):
        mac = Machine("toto.argawaen.net", "00:00:00:00:00:00", "0.0.0.0", False,
                      datetime.datetime(2020, 1, 1, 6))
        self.assertEqual(mac.get_time_str(), "2020-01-01 06:00:00")
        mac.set_time("1980-05-02 18:33:21")
        self.assertEqual(mac.get_time_str(), "1980-05-02 18:33:21")

    def test_dnsnaming(self):
        mac = Machine("toto.argawaen.net", "00:00:00:00:00:00", "0.0.0.0", False,
                      datetime.datetime(2020, 1, 1, 6))
        self.assertEqual(mac.make_dns_entry(), "toto\tIN\tA\t0.0.0.0")
        self.assertEqual(mac.make_dns_reverse_entry(), "0.0.0.0.in-addr.arpa.\tIN\tPTR\ttoto")

    def test_macCompare(self):
        self.assertTrue(mac_compare("00:00:00:00:00:00", "00:00:00:00:00:00"))
        self.assertTrue(mac_compare("02:0f:b5:00:00:00", "00:00:00:00:00:00"))
        self.assertTrue(mac_compare("00:00:00:00:00:00", "02:0f:b5:00:00:00"))
        self.assertFalse(mac_compare("00:00:00:00:00:00", "02:08:b5:00:00:00"))
        self.assertTrue(mac_compare("02:0F:B5:00:0E:EE", "18:85:00:00:0e:ee"))

    def test_is_ip(self):
        self.assertTrue(str_is_ip("0.0.0.0"))
        self.assertTrue(str_is_ip("192.168.23.10"))
        self.assertFalse(str_is_ip("192.256.23.10"))
        self.assertFalse(str_is_ip("192.168.23."))
        self.assertFalse(str_is_ip("192.168..15"))
        self.assertFalse(str_is_ip("192.168.toto.15"))
        self.assertFalse(str_is_ip("argawaen.net"))


if __name__ == '__main__':
    unittest.main()
