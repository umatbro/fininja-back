#!/usr/bin/env python

"""
Add entry to spreadsheet
"""

import sys
import argparse
import datetime as dt

import inquirer

from main import get_categories, save_cost_in_spreadsheet

YEAR = 2020

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('value', type=float)
parser.add_argument('--date', required=False, type=str, nargs='?', help='Date should be in format MM-DD')

if __name__ == '__main__':
    args = parser.parse_args()
    datetime = dt.datetime.strptime(f'{YEAR}-'+args.date, '%Y-%m-%d') if args.date else dt.datetime.today()

    value = args.value

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
            message=f'Are you sure? Add {args.value} zł to category "{selected_category.value} - {subcategory.value}"',
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
