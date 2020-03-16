from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData
from django.conf import settings


def generate_openid_sign(raw_openid):
    """
    对openid进行加加密,并返回加密后的结果
    :param raw_openid: 要加密的openid
    :return: 加密后的openid
    """
    # 1.创建加密/解密对象
    serializer = Serializer(secret_key=settings.SECRET_KEY,expires_in=600)
    # 2.包装要加密的数据为字典格式
    data = {'openid':raw_openid}
    # 3. 加密对象调用dumps() 进行加密,默认返回bytes
    secret_openid = serializer.dumps(data)
    return secret_openid.decode()

def check_out_openid(secret_openid):
    """
    对openid进行解密,并返回解密后的结果
    :param openid_sign: 要解密的openid
    :return: 解密后的openid
    """
    # 1.创建加密/解密对象
    serializer = Serializer(secret_key=settings.SECRET_KEY, expires_in=600)
    # 2.调用loads方法进行解密,解密成功返回原有字典
    try:
        data = serializer.loads(secret_openid)
        raw_openid = data.get('openid')
        return raw_openid
    except BadData as e:
        return None
