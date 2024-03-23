import base64


def encodeb32(data):
    return base64.b32encode(data.encode('utf-8')).decode('utf-8')


def decodeb32(data):
    return base64.b32decode(data).decode('utf-8')


def encodeb64(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def decodeb64(data):
    return base64.b64decode(data).decode('utf-8')
