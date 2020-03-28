from django.shortcuts import render,redirect
from django.views import View
from django import http
from django.contrib.auth import login
from django.conf import settings
from django_redis import get_redis_connection

import logging, re

from user.models import User
from .models import OAuthQQUser
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall.utils.response_code import RETCODE
from .utils import generate_openid_sign,check_out_openid
from carts.utils import merge_cart_cookie_to_redis

# 指定日志输出器为django中 的日志输出器
logger = logging.getLogger('django')

# # QQ认证的参数,QQ登录开发 过程中 需要的参数
# QQ_CLIENT_ID = '101518219'     # APPid
# QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'  # APPkey
# QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'   # 回调地址

# 1. 获取QQ登录扫码页面
class QQAuthView(View):
    def get(self,request):
        # 1.获取查询参数
        next = request.GET.get('next')
        # 2.创建QQ登录工具对象
        qq_auth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                       client_secret=settings.QQ_CLIENT_SECRET,
                       redirect_uri=settings.QQ_REDIRECT_URI,
                       state=next)
        # QQ登录url
        qq_login_url = qq_auth.get_qq_url()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','login_url':qq_login_url})
# 响应json数据,前端继续请求 qq_login_url 这个路由
# https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101518219&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8000%2Foauth_callback&state=%2F


# 登录成功后 向服务器发起如下请求
# http://www.meiduo.site:8000/oauth_callback?code=A2AA27D457D93A593F1711FF6A593AD6&state=%2F
#  用户扫码登录的回调处理,获取QQ登录认证后返回的code


# """QQ登录成功回调处理"""
class QQUserAuthView(View):
    #
    def get(self,request):
    # 1.接收查询参数
        code = request.GET.get('code')
    # 2.校验code,校验请求中是否 带回了 code里的内容
        if code is None:
            return http.HttpResponseForbidden('Lost patterns')
    # 创建QQ登录工具对象
        qq_login_obj = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                               client_secret=settings.QQ_CLIENT_SECRET,
                               redirect_uri=settings.QQ_REDIRECT_URI)

        try:
        # 通过code获取access_token
            access_token = qq_login_obj.get_access_token(code)
        # 通过access_token 获取openid
            openid = qq_login_obj.get_open_id(access_token)
        except Exception as e:
            # 当发生异常时, 使用日志输出器, 输出异常信息, 提前响应
            # logger.error指定日志输出的级别,
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')
    # 查询openid是否绑定过用户
        try:
            qq_auth_models = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 未绑定账号时,跳转到绑定页面
            # openid如何处理? 将openid存入绑定页面
            # 绑定账号页面 隐藏的输入框标签  接收openid,再和 表单标签 一起提交到服务器
            # '''< input v - model = "openid" type = "hidden" name = "openid" value = "{{ openid }}" >'''
            # 此时的openid时明文可见,不安全
            data = {'openid': generate_openid_sign(openid)}

            # openid属于用户的隐私信息，所以需要将openid签名处理，避免暴露。
            # 使用 itsdangerous

            return render(request,'oauth_callback.html',data)
        else:
            # 已绑定账号,获取openid关联的 user模型对象
            # OAuthQQUser中 user = models.ForeignKey('user.User')
            # OAuthQQUser中 user字段外键关联的是User模型对象
            user = qq_auth_models.user
            # keep status
            login(request,user)
            # 重定向到指定来源
            response = redirect(request.GET.get('state') or '/')
            # 调用合并购物车函数
            merge_cart_cookie_to_redis(request, response)
            # 将用户信息保存到cookie
            # set_cookie(self, key, value='', max_age=None, expires=None, path='/',domain=None, secure=False, httponly=False):
            response.set_cookie('username',user.username,max_age=settings.SESSION_COOKIE_AGE)
            return response
    # 课堂代码
    # def get(self,request):
    #     """Oauth2.0认证"""
    #     # 接收Authorization Code
    #     code = request.GET.get('code')
    #     if not code:
    #         return http.HttpResponseForbidden('缺少code')
    #
    #     # 创建工具对象
    #     oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI)
    #
    #     try:
    #         # 使用code向QQ服务器请求access_token
    #         access_token = oauth.get_access_token(code)
    #
    #         # 使用access_token向QQ服务器请求openid
    #         openid = oauth.get_open_id(access_token)
    #     except Exception as e:
    #         logger = logging.getLogger('django')
    #         logger.error(e)
    #         return http.HttpResponseServerError('OAuth2.0认证失败')
    #     try:
    #         oAuth_model = OAuthQQUser.objects.get(openid=openid)
    #     except OAuthQQUser.DoesNotExist:
    #         # 包装传入模板渲染的数据
    #         data = {'openid': openid}
    #         # 如果openid没有绑定用户,给用户展示绑定界面
    #         return render(request, 'oauth_callback.html', data)
    #     else:
    #         # 如果openid已绑定用户,直接代码登录成功...
    #         # 查询openid关联的user
    #         user = oAuth_model.user
    #         # 状态保持
    #         login(request, user)
    #         # 重定向到指定来源
    #         response = redirect(request.GET.get('state') or '/')
    #         # 存储cookie username
    #         response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
    #         return response
    #
    #

    # 使用openid 绑定用户
    def post(self,request):
        query_dict = request.POST
        mobile = query_dict.get('mobile')
        password = query_dict.get('password')
        image_code = query_dict.get('image_code')
        sms_code = query_dict.get('sms_code')
        # 对openid进行解密,并返回解密后的结果
        openid = check_out_openid(query_dict.get('openid'))


        if not all([mobile,password,image_code,sms_code,openid]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        if not re.match(r'^[0-9A-Za-z]{8,20}',password):
            return http.HttpResponseForbidden('请输入8-20密码')

        redis_server = get_redis_connection('verify_codes')
        redis_sms_code = redis_server.get('sms_%s' % mobile)
        if redis_sms_code is None:
            return http.HttpResponseForbidden('短信验证码已过期')
        redis_sms_code = redis_sms_code.decode()
        if sms_code != redis_sms_code:
            return http.HttpResponseForbidden('请输入正确的短信验证码')
        if openid is None:
            return http.HttpResponseForbidden('openid无效')
        try:
            user = User.objects.get(user_mobile=mobile)
        except User.DoesNotExist:
            # 如果mobile没有查询到,说明是新用户,就创建一个新user再和openid绑定
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 如果mobile能查询到,说明是已注册的老用户,再校验密码,
            if user.check_password(password) is False:
                return http.HttpResponseForbidden('QQ绑定用户失败')
        OAuthQQUser.objects.create(openid=openid,user=user)
        login(request, user)
        response = redirect(request.GET.get('state') or '/')
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
        return response

