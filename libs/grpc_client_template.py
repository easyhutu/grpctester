import re
from datetime import datetime

class_template = """
# 编译时间： {create_time} 
# package:{package_name}

import grpc
from pbs import {pb2_grpc}
from pbs import {pb2}
from settings import CRED_PATH, HOST
import json
from google.protobuf.json_format import MessageToJson


class Client:
    def __init__(self, host=None, enable_cred=False, is_cred=False, metadata=None):
        self.host = host if host else HOST
        self.is_cred = is_cred
        self.client_pb2 = {pb2}
        self.client_pb2_grpc = {pb2_grpc}
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
"""

channel_template = """
    def {channel}(self, params={req_params_format}, need_metadata=False, metadata=None):
        # channel name : {channel}
        # params: {req_params}
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
        stub = self.client_pb2_grpc.{stub_name}(channel)
        
        print('method:', stub.{channel}._method.decode())
        print('params:', str(params), '\\n')

        response, call = stub.{channel}.with_call(
            request=self.client_pb2.{req_class}(**params), metadata=metadata)
        value = MessageToJson(response)
        val_json = json.loads(value)
        metadata = [dict(name=key, value=value) for key, value in call.trailing_metadata()]

        if need_metadata:
            print('metadata: ' + str(metadata))
            return val_json, metadata
        return val_json
"""


def parse_stub(val):
    valsp = val.split(' ')
    for idx, item in enumerate(valsp):
        if item in '{':
            return valsp[idx-1]


def parse_proto(file_path):
    with open(file_path, encoding='utf8') as f:
        data = f.read()

    proto_info = dict(
        package='',
        service_rpc=[],
        stub_name=''

    )
    data = data.replace('\n', ' ').replace('\r', ' ')
    # print(data)
    package_re = 'package.*?;'  # 匹配package 包名
    result = re_comp(package_re, data)
    if result:
        proto_info['package'] = result.replace('package', '').replace(';', '')

    sername_re = 'service .*?{'  # 匹配服务
    sername_result = re_comp(sername_re, data)

    proto_info['stub_name'] = parse_stub(sername_result) + 'Stub'

    service_re = 'service.*?}'
    service_result = re_comp(service_re, data).split(';')

    for rpc in service_result:

        result_rpc = 'rpc.*?return'
        val = re_comp(result_rpc, rpc)

        if val:
            va = val.split(' ')

            chann = va[1]
            req = va[2].replace('(', '').replace(')', '')

            req_msg = f'message {req}.*?' + '}'

            msg = re_comp(req_msg, data)
            ch = {'channel': chann, 'req_cls': req}
            if msg:
                msg = msg.split('{')[-1].split('}')[0]
                ch['req_params'] = msg

                params_format = {}
                try:
                    params_list = msg.split(';')
                    for pa in params_list:
                        pa.strip()
                        key = pa.split(' =')[0].split(' ')[-1]
                        if key:
                            params_format[key] = None
                    ch['req_params_format'] = params_format
                except:
                    pass

            proto_info['service_rpc'].append(ch)

    return proto_info


def re_comp(rep, data):
    result = re.findall(rep, data)
    if len(result) > 0:
        return result[0]
    return None


def create_template_client(file_path, pname):
    proto_info = parse_proto(file_path)
    class_temp = class_template.format(create_time=datetime.now(),
                                       package_name=proto_info.get('package'),
                                       pb2_grpc=f'{pname}_pb2_grpc',
                                       pb2=f'{pname}_pb2',
                                       )

    channel_list = []
    for item in proto_info.get('service_rpc'):
        chann_fun = channel_template.format(
            channel=item.get('channel'),
            req_params=item.get('req_params'),
            stub_name=proto_info.get('stub_name'),
            req_class=item.get('req_cls'),
            req_params_format=item.get('req_params_format')
        )
        channel_list.append(chann_fun)

    value = ''.join([class_temp] + channel_list)
    return value
