#!/usr/bin/env python

"""
Manage budget.

Available commands:
* add - add entry
* show - open browser and show spreadsheet
* today - show amount spent on a given day
"""

import sys
import argparse
from argparse import RawTextHelpFormatter
import datetime as dt

import inquirer

from main import get_categories, save_cost_in_spreadsheet

YEAR = 2020

parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)

subparsers = parser.add_subparsers(dest='subparser')

parser_add = subparsers.add_parser('add')
parser_add.add_argument('value', type=float)
parser_add.add_argument('-d', '--date', required=False, type=str, nargs='?', help='Date should be in format MM-DD', dest='date')


def add(value, date):
    datetime = dt.datetime.strptime(f'{YEAR}-{date}', '%Y-%m-%d') if date else dt.datetime.today()

    print('Downloading categories list...')
    categories = dict(get_categories())

    first_question = [
        inquirer.List(
            'primary_category',
            message='Select category',
            choices=list(map(lambda cat: cat.value, categories.keys())),
        )
    ]
    answer = inquirer.prompt(first_question)
    selected_category = next(filter(lambda cat: cat.value == answer['primary_category'], categories.keys()))

    second_question = [
        inquirer.List(
            'subcategory',
            message='Select subcategory',
            choices=list(map(lambda cat: cat.value, categories[selected_category])),
        ),
    ]

    answer2 = inquirer.prompt(second_question)
    subcategory = next(filter(lambda cat: cat.value == answer2['subcategory'], categories[selected_category]))

    confirm_msg = 'Yes'
    cancel_msg = 'No, cancel'
    confirm_question = [
        inquirer.List(
            'confirm',
            message=f'Are you sure? Add {value} zł to category "{selected_category.value} - {subcategory.value}"',
            choices=(confirm_msg, cancel_msg),
        ),
    ]

    answer3 = inquirer.prompt(confirm_question)

    if answer3['confirm'] == cancel_msg:
        sys.exit(1)

    current_cell = save_cost_in_spreadsheet(
        value=value,
        category_name=selected_category.value,
        subcategory_name=subcategory.value,
        date=datetime,
    )

    if not current_cell:
        print('Error')
        sys.exit(1)


if __name__ == '__main__':
    kwargs = vars(parser.parse_args())
    subparser = kwargs.pop('subparser')
    if not subparser:
        parser.print_help()
        sys.exit(0)
    else:
        globals()[subparser](**kwargs)
