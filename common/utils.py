import json

from common.variables import MAX_LEN_MSG


def send_message(msg, sock):
    json_msg = json.dumps(msg).encode('utf-8')
    sock.send(json_msg)


def get_message(sock):
    byte_json_msg = sock.recv(MAX_LEN_MSG)
    json_msg = byte_json_msg.decode('utf-8')
    data = json.loads(json_msg)
    return data
