import grpc
from proto import helloc_pb2,helloc_pb2_grpc
from concurrent import futures
import time
import contextlib
import socket
# class Greeter(hello_pb2_grpc.GreeterServicer):
#     def SayHello(self, request, context):
#         return hello_pb2.HelloReply(message=f"你好,{request.name}")

def _abort(code,details):
    def  terminate(ignored_request,context):
        context.abort(code,details)
    return grpc.unary_unary_rpc_method_handler(terminate)

class TestInterceptor:
    def __init__(self,key,value,code,detail) -> None:
        self.key=key
        self.value=value
        self._abort=_abort(code,detail)

    def intercept_service(self,continuation,handler_call_detail):
        #函数执行器continuation
        headers =dict(handler_call_detail.invocation_metadata)
        print(headers)
        # if (self.key,self.value) not in handler_call_detail.invocation_metadata:
        #     return self._abort

        if headers.get(self.key,'')!=self.value:
            return self._abort

        return continuation(handler_call_detail)

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

    ##双向流模式
    def TestClientTwoStream(self, request_iterator, context):

        for request in request_iterator:
            data = request.data
            print(data)
            yield helloc_pb2.TestClientTwoStreamResponse(result=f'service {data}')
        
    
    def SayHello(self, request, context):
        name = request.name
        # context.set_details("haha bug")
        # context.set_code(grpc.StatusCode.DATA_LOSS)
        context.set_trailing_metadata((('name', 'aaa'), ('age', '18')))

        # raise context 
        headers = context.invocation_metadata()
        print(headers)
        context.set_compression(grpc.Compression.Gzip)
        return helloc_pb2.HelloReply()

if __name__ == '__main__':
    validator = TestInterceptor('name','deee',grpc.StatusCode.UNAUTHENTICATED,'Access denined')
    #实例化server
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        compression=grpc.Compression.Gzip,
        interceptors=(validator,),
        #发送包大小 2M 默认最大值
        options=[
            ('grpc.max_send_message_length', 50*1024*1024),
            ('grpc.max_receive_message_length', 10*1024*1024),
            ('grpc.so_reuesport', 1)
        ]
        )
    #注册逻辑1到server 中
    helloc_pb2_grpc.add_BibiliServicer_to_server(Bibili(),server)
    #启动server

    server.add_insecure_port("[::]:50052")
    print(f"[::]:50051")
    server.start()
    server.wait_for_termination()