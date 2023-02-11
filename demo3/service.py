import grpc
from proto import helloc_pb2,helloc_pb2_grpc
from concurrent import futures
import time
# class Greeter(hello_pb2_grpc.GreeterServicer):
#     def SayHello(self, request, context):
#         return hello_pb2.HelloReply(message=f"你好,{request.name}")
class Bibili(helloc_pb2_grpc.BibiliServicer):
    def TestClientRecvStream(self,request,context):
        while context.is_active():
            a=request.data
            if a =='close':
                context.cancel()
            t = time.time()
            print(f"收到 {a}")
            time.sleep(1)
            yield helloc_pb2.TestClientRecvStreamResponse(result=f'send {a} time={t}' )

    def TestClientSendStream(self, request_iterator, context):
        index=0
        for req in request_iterator:
            print(req.data)
            if index == 10:
                break
            index+=1
        return helloc_pb2.TestClientSendStreamResponse(result="c")

    def TestClientTwoStream(self, request_iterator, context):

        for request in request_iterator:
            data = request.data
            print(data)
            yield helloc_pb2.TestClientTwoStreamResponse(result=f'service {data}')

if __name__ == '__main__':
    #实例化server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #注册逻辑1到server 中
    helloc_pb2_grpc.add_BibiliServicer_to_server(Bibili(),server)
    #启动server

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()