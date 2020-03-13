from concurrent import futures
import logging

import grpc
from main import get_categories
import proto_out.category_pb2_grpc
import proto_out.category_pb2


class CategoriesService(proto_out.category_pb2_grpc.CategoriesServiceServicer):
    def getCategories(self, request, context):
        for category, subcategories in get_categories():
            yield proto_out.category_pb2.Category(name=category, subcategories=[
                proto_out.category_pb2.Category(name=subcategory) for subcategory in subcategories
            ])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_out.category_pb2_grpc.add_CategoriesServiceServicer_to_server(CategoriesService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
