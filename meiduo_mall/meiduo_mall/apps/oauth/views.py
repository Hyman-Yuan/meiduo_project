from django.shortcuts import render
from django.views import View
from django import http

import logging

from QQLoginTool.QQtool import OAuthQQ

from meiduo_mall.utils.response_code import RETCODE

# QQ认证的参数,QQ登录开发 过程中 需要的参数
QQ_CLIENT_ID = '101518219'     # APPid
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'  # APPkey
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'   # 回调地址

# 1. 获取QQ登录扫码页面
class QQAuthView(View):
    def get(self,request):
        # 1.获取查询参数
        next = request.GET.get('next')
        # 2.创建QQ登录工具对象
        qq_auth = OAuthQQ(client_id=QQ_CLIENT_ID,
                       client_secret=QQ_CLIENT_SECRET,
                       redirect_uri=QQ_REDIRECT_URI,
                       state=next)
        # QQ登录url
        qq_login_url = qq_auth.get_qq_url()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','login_url':qq_login_url})
# 响应json数据,前端继续请求 qq_login_url 这个路由
# https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101518219&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8000%2Foauth_callback&state=%2F


# 登录成功后 向服务器发起如下请求
# http://www.meiduo.site:8000/oauth_callback?code=A2AA27D457D93A593F1711FF6A593AD6&state=%2F
#  用户扫码登录的回调处理,获取QQ登录认证后返回的code

class QQUserAuthView(View):

    def get(self,request):
        """Oauth2.0认证"""
        # 接收Authorization Code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少code')

        # 创建工具对象
        oauth = OAuthQQ(client_id=QQ_CLIENT_ID, client_secret=QQ_CLIENT_SECRET, redirect_uri=QQ_REDIRECT_URI)

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger = logging.getLogger('django')
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')
        pass

