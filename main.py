from decimal import Decimal
from collections import deque
import datetime as dt

import yaml
import gspread
from google.protobuf.timestamp_pb2 import Timestamp
from oauth2client.service_account import ServiceAccountCredentials

from proto_out.category_pb2 import Category


EMPTY_CELL_VALUE = '.'
CELL_RANGE = 'B14:B213'
with open('secrets.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
SPREADSHEET_KEY = config['spreadsheet_key']
KEYFILE_PATH = config['keyfile_path']

DATES_COLUMNS_START_COLUMN_NUMBER = 8

MONTHS_MAPPING = {
    1: 'styczeń',
    2: 'luty',
    3: 'marzec',
    4: 'kwiecień',
    5: 'maj',
    6: 'czerwiec',
    7: 'lipiec',
    8: 'sierpień',
    9: 'wrzesień',
    10: 'październik',
    11: 'listopad',
    12: 'grudzień',
}


def get_worksheets():
    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE_PATH, scopes)

    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
    return spreadsheet.worksheets()


def get_categories():
    worksheets = get_worksheets()

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
        category = cells[0]
        subcategories = [cell for cell in cells[1:] if cell.value != EMPTY_CELL_VALUE]
        yield category, subcategories


def add_value_to_formula(value, current_cell_value: str = ''):
    """
    Add a new spend value to the cell. If cell already had some spending, add this as another entry
    :param value: Value to be inserted
    :param current_cell_value:
    :return: correct formula
    """
    str_val = str(Decimal(abs(value)).quantize(Decimal('0.01'))).replace('.', ',')
    sign = '+' if value >= 0 else '-'
    return ('' if current_cell_value.startswith('=') else '=') + \
        current_cell_value + sign + str_val


def put_cost_in_spreadsheet(value, category: Category, timestamp: Timestamp):
    if not category.subcategories:
        raise ValueError('No subcategory chosen.')
    date = dt.datetime.fromtimestamp(timestamp.seconds)
    category_name = category.name
    subcategory_name = category.subcategories[0].name
    worksheets = get_worksheets()
    curr_month_worksheet = next(filter(
        lambda worksheet: MONTHS_MAPPING[date.month] in worksheet.title.lower(),
        worksheets,
    ))
    if not curr_month_worksheet:
        return

    categories_column = deque(curr_month_worksheet.range('B51:B251'))

    parent_category_encountered = False
    row_to_modify = None
    while categories_column:
        category_cell = categories_column.popleft()
        if category_cell.value == category_name:
            parent_category_encountered = True
        elif category_cell.value == subcategory_name and parent_category_encountered:
            # this is the row we want
            row_to_modify = category_cell.row
            break

    if not row_to_modify:
        raise ValueError('Row to modify could not be found')

    column_to_modify = DATES_COLUMNS_START_COLUMN_NUMBER + date.day
    current_cell = curr_month_worksheet.cell(row_to_modify, column_to_modify, value_render_option='FORMULA')
    value_to_put = add_value_to_formula(value, current_cell_value=current_cell.value)
    curr_month_worksheet.update_cell(row_to_modify, column_to_modify, value_to_put)
    return current_cell
