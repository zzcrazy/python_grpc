# python_grpc
from learn grpc , practice write python code

##  grpc库安装
```
python -m pip install grpcio #安装grpc
python -m pip install grpcio-tools #安装grpc tools
```

proto make 
```
python -m grpc_tools.protoc --python_out=./proto --grpc_python_out=./proto -I./proto helloc.proto
```

### grpc 数据交互方式
* 简单模式
* 服务端数据流模式
* 客户端数据流模式
* 双向数据流模式
