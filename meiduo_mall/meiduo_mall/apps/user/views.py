from django.shortcuts import render
from django.views import View
# Create your views here.
from user.models import User
from django import http
import re
from django.contrib.auth import login

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
        # password = query_dict.password
        # password2 = query_dict.password2
        # mobile = query_dict.mobile
        # # image_code = query_dict.image_code
        # sms_code = query_dict.sms_code
        # allow = query_dict.allow
        username = query_dict.get('username')
        password = query_dict.get('password')
        password2 = query_dict.get('password2')
        mobile = query_dict.get('mobile')
        image_code = query_dict.get('image_code')
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

        # AbstractUser中自定义了 UserManager(),管理器中实现了 create_user方法,该方法将 create,set_password,save 进行了封装,简化了代码
        #  # notice the parameters and attributes in User class.
        user = User.objects.create_user(username=username,password=password,user_mobile=mobile)
        # django自带的模块 login实现状态保持,logout实现退出登录,基于cookie和session实现的
        login(request,user)

        return http.HttpResponse('Register successfull')


