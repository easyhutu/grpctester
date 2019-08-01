import os

# 项目根地址
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
_CREDS_PATH = os.path.join(PROJECT_ROOT, 'creds')

PB_PATH = os.path.join(PROJECT_ROOT, 'pbs')

PROTO_PATH = os.path.join(PB_PATH, 'protos')

CRED_PATH = os.path.join(_CREDS_PATH, 'root.crt')

# host localhost:5001
HOST = ''