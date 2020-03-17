from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData

from django.conf import settings

from .models import User

# 获取用户账号
def get_account(account):
    try:
        user = User.objects.get(username=account)
        return user
    except User.DoesNotExist:
        try:
            user = User.objects.get(user_mobile=account)
            return user
        except User.DoesNotExist:
            return None

# 自定义认证后端类
class AccountAuthBackend(ModelBackend):
    """自定义用户认证后端类"""
    # 重写ModelBackend父类的authenticate方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1.动态的根据用户名或手机号查询用户
        user = get_account(username)
        # 2.校验用户密码
        if user and user.check_password(password):
            return user
            # 返回user


def generate_email_verify_url(user):
    # # 创建加密/解密对象
    serializer = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
    # 需要加密内容
    data = {'id':user.id,'email':user.email}
    # 使用serializer对象将data加密，并转成字符串格式
    token = serializer.dumps(data).decode()
    # 拼接邮箱验证的连接
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token

    return verify_url

def check_out_user_email(token):
    serializer = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    try:
        data = serializer.loads(token)
        user_id = data.get('id')
        user_email = data.get('email')
        try:
            user = User.objects.get(id=user_id,email=user_email)
            return user
        except:
            return None
    except:
        return None

