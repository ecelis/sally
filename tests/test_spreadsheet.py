import unittest
import datetime
import logging
from googleapiclient.errors import HttpError
import crabs.sally.google.spreadsheet as gs

logger = logging.getLogger(__name__)

csvs = ['./tests/fixtures/mx.csv',
            './tests/fixtures/sampleab.csv']

class SpreadsheetTestCase(unittest.TestCase):

    def setUp(self):
        self.spreadsheetId = '1AxioUWtPJItfnv--JxNg5-oiUUMJgW4uoQopx-JlH00'
        self.sheet = 'testing'
        self.sheet_rows = [
                [0.5,
                'www.test.com',
                'keywords,here',
                '800-234-1234',
                'example@mail.com',
                'somEcommerce',
                'Place',
                '01/09/2018']
                ]

        self.expected_result = {'spreadsheetId': self.spreadsheetId,
                'updatedCells': 8, 'updatedRange': 'testing!A2:H2',
                'updatedRows': 1, 'updatedColumns': 8}

        self.bad_rows = [
                [
                'www.test.com',
                'keywords,here',
                '800-234-1234',
                'example@mail.com',
                'somEcommerce',
                'Place',
                '01/09/2018']
                ]


    def test_get_spreadsheet(self):
        response = gs.get_spreadsheet(self.spreadsheetId)
        self.assertEqual(response['spreadsheetUrl'],
                'https://docs.google.com/a/skydrop.com.mx/spreadsheets/d/1AxioUWtPJItfnv--JxNg5-oiUUMJgW4uoQopx-JlH00/edit')


    def test_insert_to(self):
        """Test insert data to spreadsheet"""
        self.assertEqual(
                gs.insert_to(self.spreadsheetId, self.sheet, self.sheet_rows, 2),
                self.expected_result)


    @unittest.expectedFailure
    def test_bad_insert(self):
        self.assertEqual(
                gs.insert_to(self.spreadsheetId, self.sheet, self.bad_rows, 2),
                self.expected_result, "Bad row")



    def test_create_sheet(self):
        """Test create spreadsheet"""
        try:
            response = gs.insert_to(self.spreadsheetId, '1',
                    self.sheet_rows, 2)
            return response
        except HttpError as err:
            print(err.error_details)
            title = str(datetime.datetime.now())
            ex_response = gs.create_sheet(self.spreadsheetId, title)
            self.assertEqual(
                    ex_response['replies'][0]['addSheet']['properties']['title'],
                    title)

            return ex_response

    def test_create_spreadsheet(self):
        response = gs.create_spreadsheet('test')
        logger.info(response)
        self.assertEqual(type(response), dict)

if __name__ == '__main__':
    unittest.main()
