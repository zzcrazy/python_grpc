from proto import hello_pb2


request = hello_pb2.HelloRequest()

request.name = "bobby"
req_str = request.SerializeToString()
print(req_str)

request2 = hello_pb2.HelloRequest()

request2.ParseFromString(req_str)
print(request2.name)
import json
req_json = {
    "name":"bobby"
}
print(len(json.dumps(req_json)))
print(len(req_str))