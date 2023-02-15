import grpc
from proto import helloc_pb2,helloc_pb2_grpc
from concurrent import futures
import time
import contextlib
import socket
import sys
import multiprocessing
import datetime

_PROCESS_COUNT =  4
_THREAD_CONCURRENCY=_PROCESS_COUNT
_ONE_DAY=datetime.timedelta(days=1)

def _abort(code,details):
    def  terminate(ignored_request,context):
        context.abort(code,details)
    return grpc.unary_unary_rpc_method_handler(terminate)


@contextlib.contextmanager
def _reserve_port():
    '''
    so_reuseport 安装grpcio的时候需要按照上边的这种模式进行编译安装
    '''
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(('', 0))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()

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
#grpc 服务
def serv(port='50051'):
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

    server.add_insecure_port(f"[::]:{port}")
    print(f"[::]:{port}")
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        server.stop(None)

def main():
    with _reserve_port() as port:
        print(port)
        sys.stdout.flush()
        workers = []
        for _ in range(_PROCESS_COUNT):
            # NOTE: It is imperative that the worker subprocesses be forked before
            # any gRPC servers start up. See
            # https://github.com/grpc/grpc/issues/16001 for more details.
            worker = multiprocessing.Process(target=serv,
                                             args=(50052,))
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()

if __name__ == '__main__':
    main()