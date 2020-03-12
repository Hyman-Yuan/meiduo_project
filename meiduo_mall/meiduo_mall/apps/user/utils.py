from django.contrib.auth.backends import ModelBackend


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

