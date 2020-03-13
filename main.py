from collections import deque

import yaml

import gspread
from oauth2client.service_account import ServiceAccountCredentials


EMPTY_CELL_VALUE = '.'
CELL_RANGE = 'B14:B213'
with open('secrets.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
SPREADSHEET_KEY = config['spreadsheet_key']
KEYFILE_PATH = config['keyfile_path']


def get_categories():
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE_PATH, scopes)

    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
    worksheets = spreadsheet.worksheets()

    categories_worksheet = next(filter(lambda worksheet: worksheet.title == 'Wzorzec kategorii', worksheets))
    categories_column = categories_worksheet.range(CELL_RANGE)

    def split_lists(list_: list, separator=''):
        dq = deque(list_)
        items = []
        while dq:
            item = dq.popleft()
            if item.value.strip() == separator:
                yield tuple(items)
                items = []
            else:
                items.append(item)

        if items:
            yield tuple(items)

    income = categories_column[:16]
    spendings = list(split_lists(categories_column[21:]))

    for cells in [tuple(income)] + spendings:
        category = cells[0].value
        subcategories = [cell.value for cell in cells[1:] if cell.value != EMPTY_CELL_VALUE]
        yield category, subcategories
