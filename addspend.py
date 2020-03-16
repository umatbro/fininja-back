"""
Add entry using Remote Procedure Call
"""

import sys
import argparse
import datetime as dt

import inquirer
import grpc
import proto_out.category_pb2_grpc
import proto_out.category_pb2
from google.protobuf.timestamp_pb2 import Timestamp

YEAR = 2020

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('value', default=0.0, type=float, nargs='?')
parser.add_argument('--date', required=False, type=str, nargs='?', help='Date should be in format MM-DD')

if __name__ == '__main__':
    args = parser.parse_args()
    datetime = dt.datetime.strptime(f'{YEAR}-'+args.date, '%Y-%m-%d') if args.date else dt.datetime.today()

    print('Downloading categories list...')
    channel = grpc.insecure_channel('localhost:50051')
    stub = proto_out.category_pb2_grpc.SpreadsheetServiceStub(channel)
    response = stub.getCategories(proto_out.category_pb2.GetCategoriesParams())

    categories = list(response)

    first_question = [
        inquirer.List(
            'primary_category',
            message='Select category',
            choices=list(map(lambda cat: cat.name, categories)),
        )
    ]
    answer = inquirer.prompt(first_question)
    selected_category = next(filter(lambda cat: cat.name == answer['primary_category'], categories))

    second_question = [
        inquirer.List(
            'subcategory',
            message='Select subcategory',
            choices=list(map(lambda cat: cat.name, selected_category.subcategories)),
        ),
    ]
    answer2 = inquirer.prompt(second_question)
    subcategory = next(filter(lambda cat: cat.name == answer2['subcategory'], selected_category.subcategories))
    del selected_category.subcategories[:]
    selected_category.subcategories.append(subcategory)

    request = proto_out.category_pb2.CostEntryRequest(costEntry=proto_out.category_pb2.CostEntry(
        category=selected_category,
        amount=args.value,
        timestamp=Timestamp(seconds=int(datetime.timestamp())),
    ))

    confirm_msg = 'Yes'
    cancel_msg = 'No, cancel'
    confirm_question = [
        inquirer.List(
            'confirm',
            message=f'Are you sure? Add {args.value} zł to category "{selected_category.name} - {subcategory.name}"',
            choices=(confirm_msg, cancel_msg),
        ),
    ]

    answer3 = inquirer.prompt(confirm_question)

    if answer3['confirm'] == cancel_msg:
        sys.exit(1)

    response = stub.putCostEntry(request)
    print(response.message)
    if response.errorOccurred:
        sys.exit(1)
