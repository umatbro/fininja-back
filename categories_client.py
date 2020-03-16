import grpc
import proto_out.category_pb2_grpc
import proto_out.category_pb2


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = proto_out.category_pb2_grpc.SpreadsheetServiceStub(channel)
    response = stub.getCategories(proto_out.category_pb2.GetCategoriesParams())

    for val in response:
        print(val.name, [subcategory.name for subcategory in val.subcategories])


if __name__ == '__main__':
    run()
