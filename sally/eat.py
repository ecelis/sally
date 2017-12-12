import csv
from pathlib import Path


def check_path(files, verified=[]):
    """Check files in list exists and can be read to avoid failures"""
    if not files:
        return verified

    csv_file = Path(files.pop())
    if csv_file.is_file():
        verified.append(csv_file)

    return check_path(files, verified)



def feed_csv(files, delimiter=',', **kwargs):
    """Read a set of CSV files with URLs"""
    if type(files) is not list:
        raise TypeError('files parameter should be a list.')


