from proto import helloc_pb2,helloc_pb2_grpc
import grpc
import time
import random
def test():
    index = 1
    while True:
        time.sleep(1)
        data = str(random.random())
        if index ==5:
            break
        index+=1
        yield helloc_pb2.TestClientSendStreamRequest(data=data)
if __name__ == '__main__':

    with grpc.insecure_channel("127.0.0.1:50052") as channel:
        stub =helloc_pb2_grpc.BibiliStub(channel)

        try:

            # resp = stub.SayHello(helloc_pb2.HelloRequest(name='22'))

            #获取metedata 数据
            resp,call= stub.SayHello.with_call(helloc_pb2.HelloRequest(name='22'),
            compression=grpc.Compression.Gzip,
            metadata=(('client_key','client_value'),))
            
            print(resp.result)
            headers = call.trailing_metadata()
            print(headers[0].key,headers[0].value)
            for v in  headers:
                print(v.key,v.value)
        except Exception as e:
            print(11,e.code().name,e.code().value,e.details())
        #静态设置
        #单向服务端流请求
        # rsp: helloc_pb2.TestClientRecvStreamResponse= stub.TestClientRecvStream(helloc_pb2.TestClientRecvStreamRequest(data=f"close"))
        # for item in rsp:s
        #     print(item.result)

        #单向客户端流请求
        # res = stub.TestClientSendStream(test())
        # print(res)

        #双向流
        # res = stub.TestClientTwoStream(test())
        # for d in res:
        #     print(d.result)