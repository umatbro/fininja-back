from concurrent import futures
import logging
import datetime as dt

import grpc
from main import get_categories, put_cost_in_spreadsheet
import proto_out.category_pb2_grpc
import proto_out.category_pb2


class SpreadsheetService(proto_out.category_pb2_grpc.SpreadsheetServiceServicer):
    def getCategories(self, request, context):
        for category, subcategories in get_categories():
            yield proto_out.category_pb2.Category(name=category.value,  subcategories=[
                proto_out.category_pb2.Category(name=subcategory.value) for subcategory in subcategories
            ])

    def putCostEntry(self, request: proto_out.category_pb2.CostEntryRequest, context):
        if not request.costEntry:
            return proto_out.category_pb2.CostEntryResponse(
                message='costEntry: this field is required',
                errorOccurred=True,
            )
        message = ''
        errorOccurred = False

        try:
            put_cost_in_spreadsheet(
                value=request.costEntry.amount,
                category=request.costEntry.category,
                timestamp=request.costEntry.timestamp,
            )
        except ValueError as e:
            message = str(e)
            errorOccurred = True
        else:
            message = 'success'
        finally:
            return proto_out.category_pb2.CostEntryResponse(
                message=message,
                errorOccurred=errorOccurred,
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_out.category_pb2_grpc.add_SpreadsheetServiceServicer_to_server(SpreadsheetService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
