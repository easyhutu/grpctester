
# 编译时间： 2019-08-02 11:38:59.267181 
# package: = "io.grpc.examples.helloworld"

import grpc
from pbs import helloword_pb2_grpc
from pbs import helloword_pb2
from settings import CRED_PATH, HOST
import json
from google.protobuf.json_format import MessageToJson


class Client:
    def __init__(self, host=None, enable_cred=False, is_cred=False, metadata=None):
        self.host = host if host else HOST
        self.is_cred = is_cred
        self.client_pb2 = helloword_pb2
        self.client_pb2_grpc = helloword_pb2_grpc
        self.metadata = metadata
        self.enable_cred = enable_cred

    @staticmethod
    def _parse_metadata(metadata):
        if metadata:
            meta_list = []
            for key in metadata.keys():
                meta_list.append([key, metadata[key]])
            return meta_list
        else:
            return metadata

    def SayHello(self, params={'name': None}, need_metadata=False, metadata=None):
        # channel name : SayHello
        # params:    string name = 1; 
        # need_metadata： 是否返回metadata

        with open(CRED_PATH, 'rb') as f:
            if self.is_cred:
                cred = grpc.ssl_channel_credentials(f.read())
            else:
                cred = grpc.ssl_channel_credentials()
        
        if metadata:
            self.metadata.update(metadata)
        metadata = self._parse_metadata(self.metadata)
        
        if self.enable_cred:
            channel = grpc.secure_channel(self.host, cred)
        else:
            channel = grpc.insecure_channel(self.host)
        stub = self.client_pb2_grpc.GreeterStub(channel)
        
        print('method:', stub.SayHello._method.decode())
        print('params:', str(params), '\n')

        response, call = stub.SayHello.with_call(
            request=self.client_pb2.HelloRequest(**params), metadata=metadata)
        value = MessageToJson(response)
        val_json = json.loads(value)
        metadata = [dict(name=key, value=value) for key, value in call.trailing_metadata()]

        if need_metadata:
            print('metadata: ' + str(metadata))
            return val_json, metadata
        return val_json
