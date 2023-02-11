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

    with grpc.insecure_channel("127.0.0.1:50051") as channel:
        stub =helloc_pb2_grpc.BibiliStub(channel)
        #静态设置
        #单向服务端流请求
        # rsp: helloc_pb2.TestClientRecvStreamResponse= stub.TestClientRecvStream(helloc_pb2.TestClientRecvStreamRequest(data=f"close"))
        # for item in rsp:
        #     print(item.result)

        #单向客户端流请求
        # res = stub.TestClientSendStream(test())
        # print(res)

        #双向流
        res = stub.TestClientTwoStream(test())
        for d in res:
            print(d.result)