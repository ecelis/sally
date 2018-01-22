import os
import unittest
import datetime
from googleapiclient.errors import HttpError
import sally.google.drive as gd

class DriveTestCase(unittest.TestCase):

    def setUp(self):
        pass


    def test_get_uploads(self):
        response = gd.get_uploads(os.environ.get('DRIVE_UPLOADS'))
        print(response)
        self.assertEqual(type(response), list)


    def test_get_file(self):
        response = gd.get_file(file_id)
        self.assertEqual(response, 'something')
