import numpy as np
import pandas as pd
import validators
from pathlib import Path


def check_path(files, verified=[]):
    """Check files in list exists and can be read to avoid failures"""
    if not files:
        return verified

    csv_file = Path(files.pop())
    if csv_file.is_file():
        verified.append(csv_file)

    return check_path(files, verified)


def feed_csv(files, col=0, delimiter=',', urls=np.array([])):
    """Read a set of CSV files with URLs"""
    if not files:
        return urls

    f = files.pop()
    # TODO validate url
    if len(urls) < 0:
        print('0 dim')
        urls = pd.read_csv(f, sep=delimiter, error_bad_lines=False,
                header=None, index_col=False, names=['url'], usecols=['url'],
                memory_map=True).values
    else:
        print('>0 dim')
    # TODO validate url
        np.concatenate((urls,
                pd.read_csv(f, sep=delimiter, error_bad_lines=False,
                header=None, index_col=False, names=['url'], usecols=['url'],
                memory_map=True).values
                ))

    return feed_csv(files, col=col, delimiter=delimiter, urls=urls)
