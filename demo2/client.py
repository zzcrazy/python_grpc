from proto import hello_pb2,hello_pb2_grpc
import grpc
if __name__ == '__main__':

    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        stub =hello_pb2_grpc.GreeterStub(channel)
        #静态设置
        rsp: hello_pb2.HelloReply= stub.SayHello(hello_pb2.HelloRequest(name="cchendengli"))
        print(rsp.message)


