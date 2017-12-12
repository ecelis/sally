import unittest
import eat

class FeedSallyTestCase(unittest.TestCase):
    def test_check_path(self):
        self.assertIsInstance(eat.check_path(['http://www.liverpool.com.mx',
            'http://sat.gob.mx']), list)
