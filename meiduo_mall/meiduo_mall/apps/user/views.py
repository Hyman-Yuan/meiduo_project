from django.shortcuts import render
from django.views import View
from django import http
from django.contrib.auth import login, authenticate
from django_redis import get_redis_connection

import re

from user.models import User
from meiduo_mall.utils.response_code import RETCODE

class RegisterView(View):

    def get(self,request):

        return render(request,'register.html')

    # register logic
    def post(self,request):
        # post方法提交的数据使用 request.POST 接收,返回一个query_dict 对象.
        # 返回一个QueryDict对象.类似字典  通过 .get('key') 获取到 key所对应的值.
        query_dict = request.POST
        """
        # 将注册界面传入的数据全部获取到,再进行校验
        # print(query_dict)
        # query_dict('key') 当key不存在时,会出错.
        # 和query_dict.get('key') 当key不存在时,其返回结果为None,所以一般使用此方法获取前端传入的结果.  
        # 用法与字典的取值相似,但有区别  
        # 字典只会取出 key所对应的value,
        # QueryDict.get 则会取出key所对应 value列表[] 中的元素
        """
        """AttributeError: 'QueryDict' object has no attribute 'username'"""
        # username = query_dict.username

        username = query_dict.get('username')
        password = query_dict.get('password')
        password2 = query_dict.get('password2')
        mobile = query_dict.get('mobile')
        image_code = query_dict.get('image_code')
        # TODO: Verify the SMS verification code(校验短信验证码)
        sms_code = query_dict.get('sms_code')
        allow = query_dict.get('allow')


        if all([username,password,password2,mobile,sms_code,allow]) is False:
            return http.HttpResponseForbidden('please make sure all the parameter is not blank')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$',password):
            return http.HttpResponseForbidden('请输入8-20个字符的密码')
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('请输入正确格式的手机号')
        # create user by the original ways
        # 创建用户
        # user = User.objects.create(username=username,password=password,mobile=mobile)
        # 对密码进行加密
        # user.set_password(password)
        # 保存.提交到 mysql数据库
        # user.save()


        # TODO: 短信验证码校验逻辑,后期补充
        redis_cli = get_redis_connection('verify_codes')
        # !!! redis中存储的数据是byte类型,must decode()
        sms_code_server = redis_cli.get('sms_%s' % mobile).decode()
        if sms_code_server is None:
            return render(request,'register.html',{'error_image_code':'短信验证码已过期'})
        if sms_code != sms_code_server:
            return render(request, 'register.html', {'error_image_code': '短信验证码错误'})

        # AbstractUser中自定义了 UserManager(),管理器中实现了 create_user方法,该方法将 create,set_password,save 进行了封装,简化了代码
        #  # notice the parameters and attributes in User class.
        user = User.objects.create_user(username=username,password=password,user_mobile=mobile)
        # django自带的模块 login实现状态保持,logout实现退出登录,基于cookie和session实现的
        login(request,user)

        return http.HttpResponse('Register successfull')

#  /usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
# 当鼠标点击用户名输入框之外的区域,浏览器会再次发送一个请求
# register.html :
#               <input type="text" name="username" id="user_name" v-model="username" @blur="check_username">
# register.js  check_username:
#              var url = this.host + '/usernames/' + this.username + '/count/';
#                 axios.get(url, {responseType: 'json'})

class UsernameCountView(View):
        # 类视图中 get方法 传入参数时,取决于 正则组 的的写法
        # 正则组 未取别名 则按位置传参,如果有别名,则按正则组的别名进行传参
    def get(self,request,username):
        # ORM模型 增删改查  通过 模型类 实现的,通过用户名查询数据库中该用户名是否存在
        count = User.objects.filter(username=username).count()

        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','count':count})

# be similar to UsernameCountView
class MobileCountView(View):

    def get(self,request,mobile):
        count = User.objects.filter(user_mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class LoginView(View):
    '''登录功能'''
    def get(self,request):
        return render(request,'login.html')   # 登录页面

    def post(self,request):

        query_dict = request.POST
        username = query_dict.get('username')
        password = query_dict.get('password')
        remembered = query_dict.get('remembered')    # # 记住登录,非必勾项  勾选时'on' 未勾选时 None
        if not all([username,password]):
            return http.HttpResponseForbidden('error')


        # # login by username
        # # method 1
        # try:
        #     user = User.objects.get(username=username)
        #     # user.check_password(password): user 模型类 中实现校验密码的一种方法
        #     if not user.check_password(password):
        #         #结响应html的js请求
        #         return render(request,'login.html',{'account_errmsg':'用户名或密码不正确'})
        # except User.DoesNotExist:
        #     return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})

        # # method 2
        # # 用户认证,通过认证返回当前user模型否则返回None!! attention the result of authenticate (user module or None)
        user = authenticate(request,username=username,password=password)
        if not user:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})
        #

        # keep status,default two weeks
        login(request,user)
        # session 设置为0 和cookie的None都代表关闭浏览器就删除
        if remembered is None:
            request.session.set_expiry(0)  # 状态保持 不勾选,则session 设置0 或者 cookie 设置为None,cookie && session 的有效期截止于关闭浏览器
        else:
            request.session.set_expiry(3600*24*7)  # 勾选状态保持,设置自定义 的 用户登录状态保持的时间
        return http.HttpResponse('login successful')







