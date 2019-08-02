import argparse


# 解析命令行参数
def arg_proto_filename():
    parser = argparse.ArgumentParser(description="proto file name")
    parser.add_argument('--file', '-f', type=str, help='proto file name')
    parse = parser.parse_args()
    module_name = parse.file
    if module_name:
        return module_name
    else:
        raise Exception('参数错误，或者项目中不存在')
