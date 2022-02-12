import json

from common.variables import MAX_LEN_MSG, ENCODE


def send_message(msg, sock):
    json_msg = json.dumps(msg).encode(ENCODE)
    sock.send(json_msg)


def get_message(sock):
    byte_json_msg = sock.recv(MAX_LEN_MSG)
    json_msg = byte_json_msg.decode(ENCODE)
    data = json.loads(json_msg)
    return data
