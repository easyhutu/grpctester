from lib.arg_parse import arg_proto_filename
import sys
from settings import PB_PATH, PROTO_PATH
import os
from lib.grpc_client_template import create_template_client


proto_cmd = 'python -m grpc_tools.protoc --python_out={} --grpc_python_out={} -I{} {}'


def add_from(path):
    with open(path, encoding='utf8') as f:
        data = f.readlines()

    new_list = []
    for item in data:
        if item.startswith('import') and 'import grpc' not in item:
            new_list.append('from pbs {}'.format(item))
            print(new_list[-1])
        else:
            new_list.append(item)

    with open(path, 'w', encoding='utf8') as f:
        f.writelines(new_list)
    print('add from success')


if __name__ == '__main__':
    proto_filename = arg_proto_filename()
    proto_file = os.path.join(PROTO_PATH, proto_filename)
    cmd = proto_cmd.format(PB_PATH, PB_PATH, PROTO_PATH, proto_file)
    print(cmd)
    os.system(cmd)
    pname = proto_filename.split('.')[0]
    print(f'{proto_filename} compile success')
    pb2_path = os.path.join(PB_PATH, '{}_pb2_grpc.py'.format(pname))
    if pb2_path:
        add_from(pb2_path)
        client_value = create_template_client(proto_file, pname)
        client_path = os.path.join(PB_PATH, f'{pname}_client.py')
        print(f'create path: {client_path}')
        with open(client_path, 'w', encoding='utf8') as f:
            f.write(client_value)
            print(f'create client script success')



