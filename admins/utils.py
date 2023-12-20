import datetime

#重写tokenpayload里的内容
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'id': user.id,
    }