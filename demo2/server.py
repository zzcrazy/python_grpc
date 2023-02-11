import grpc
from proto import hello_pb2,hello_pb2_grpc
from concurrent import futures
class Greeter(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        return hello_pb2.HelloReply(message=f"你好,{request.name}")



if __name__ == '__main__':
    #实例化server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #注册逻辑1到server 中
    hello_pb2_grpc.add_GreeterServicer_to_server(Greeter(),server)
    #启动server

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()