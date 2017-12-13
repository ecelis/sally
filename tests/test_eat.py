import unittest
import numpy as np
import eat


csvs = ['./tests/fixtures/sampleaa.csv',
            './tests/fixtures/sampleab.csv']

class FeedSallyTestCase(unittest.TestCase):
    """Test check_path"""
    def test_check_path(self):
        self.assertIsInstance(eat.check_path(csvs), list)

    def test_feed_csv(self):
        """Test reading csv files"""
        self.assertIsInstance(eat.feed_csv(eat.check_path(files=csvs),
            delimiter=','), np.ndarray)
