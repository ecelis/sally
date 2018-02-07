import os
import unittest
import datetime
from googleapiclient.errors import HttpError
import crabs.sally.google.drive as gd

class DriveTestCase(unittest.TestCase):

    def setUp(self):
        pass


    def test_get_uploads(self):
        response = gd.get_uploads(os.environ.get('DRIVE_UPLOADS'))
        self.assertEqual(type(response), list)


    @unittest.expectedFailure
    def test_mv(self):
        response = gd.mv('1OmdlDZrbbKI79JO91M_4dCkXpCJtSB7zx8MjO9S_Gcg',
                os.environ.get('DRIVE_DONE'))
        self.assertEqual(type(response), dict or None)


    @unittest.expectedFailure
    def test_get_file(self):
        # TODO
        response = gd.get_file(file_id)
        self.assertEqual(response, 'something')
