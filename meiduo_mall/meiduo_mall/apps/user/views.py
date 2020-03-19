from django.shortcuts import render, redirect
from django.views import View
from django import http
from django.contrib.auth import login, authenticate, logout
from django_redis import get_redis_connection
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail

import re, json, logging

from user.models import User,Address
from celery_tasks.send_email.tasks import send_verify_email
from .utils import generate_email_verify_url, check_out_user_email
from meiduo_mall.utils.response_code import RETCODE
from  meiduo_mall.utils.views import LoginRequiredView

logger = logging.getLogger('django')

class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

    # register logic
    def post(self, request):
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

        if all([username, password, password2, mobile, sms_code, allow]) is False:
            return http.HttpResponseForbidden('please make sure all the parameter is not blank')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[a-zA-Z0-9_]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20个字符的密码')
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
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
            return render(request, 'register.html', {'sms_code_error': '短信验证码已过期'})
        if sms_code != sms_code_server:
            return render(request, 'register.html', {'sms_code_error': '短信验证码错误'})

        # AbstractUser中自定义了 UserManager(),管理器中实现了 create_user方法,该方法将 create,set_password,save 进行了封装,简化了代码
        #  # notice the parameters and attributes in User class.
        user = User.objects.create_user(username=username, password=password, user_mobile=mobile)
        # django自带的模块 login实现状态保持,logout实现退出登录,基于cookie和session实现的
        login(request, user)
        response = redirect('/')
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
        return response


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
    def get(self, request, username):
        # ORM模型 增删改查  通过 模型类 实现的,通过用户名查询数据库中该用户名是否存在
        count = User.objects.filter(username=username).count()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


# be similar to UsernameCountView
class MobileCountView(View):

    def get(self, request, mobile):
        count = User.objects.filter(user_mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class LoginView(View):
    '''登录功能'''

    def get(self, request):
        return render(request, 'login.html')  # 登录页面

    def post(self, request):

        query_dict = request.POST
        username = query_dict.get('username')
        account = query_dict.get('username')
        password = query_dict.get('password')
        remembered = query_dict.get('remembered')  # # 记住登录,非必勾项  勾选时'on' 未勾选时 None
        if not all([username, password]):
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
        # #
        # # 用户认证,通过认证返回当前user模型否则返回None!! attention the result of authenticate (user module or None)
        # user = authenticate(request,username=username,password=password)
        # if not user:
        #     return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})

        # # 优化升级:实现多账号登录

        # method 1:  Ues Q object get User object.
        # try:
        #     user = User.objects.get(Q(username=username) | Q(user_mobile=username))
        #     if not user.check_password(password):
        #         return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})
        # except User.DoesNotExist:
        #     return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})

        # # method 2: use try nesting
        # try:
        #     user = User.objects.get(username=account)
        #     if not user.check_password(password):
        #         return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})
        # except User.DoesNotExist:
        #     user = User.objects.get(user_mobile=account)
        #     if not user.check_password(password):
        #         return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})

        # # method 3:重写authenticate方法
        # 用户认证,通过认证返回当前user模型否则返回None
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码不正确'})

        # keep status,default two weeks
        login(request, user)
        # session 设置为0 和cookie的None都代表关闭浏览器就删除
        if remembered is None:
            request.session.set_expiry(0)  # 状态保持 不勾选,则session 设置0 或者 cookie 设置为None,cookie && session 的有效期截止于关闭浏览器
        else:
            request.session.set_expiry(3600 * 24 * 7)  # 勾选状态保持,设置自定义 的 用户登录状态保持的时间

        # return http.HttpResponse('login successful')

        # 重定向
        # return http.HttpResponse('登录成功去到首页')
        # response = redirect('/')  # 重定向到首页
        response = redirect(request.GET.get('next') or '/')
        # if remembered is None:
        #     response.set_cookie('username', user.username, max_age=None)  # cookie过期时间指定为None代表会话结束
        # else:
        #     response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)  # cookie过期时间指定为None代表会话结束
        # 登录成功向用户浏览器cookie中存储username
        response.set_cookie('username',
                            user.username,
                            max_age=None if (
                                        remembered is None) else settings.SESSION_COOKIE_AGE)  # cookie过期时间指定为None代表会话结束
        # 三目: 条件返回值 if 条件 else 不成立时返回值
        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 1. 清除状态保持
        logout(request)
        # 2. 清除cookie中的username
        response = redirect('/login/')
        response.delete_cookie('username')
        # 3. 重定向到login界面
        return response


#
class InfoView(LoginRequiredMixin, View):
    """用户中心"""

    # def get(self, request):
    #     # 判断当前请求用户是否登录

    #     method 1
    #     # isinstance(对象, 类名)  # 判断对象是否有 指定的类或子类创建出来的对象
    #     # if isinstance(request.user, User):

    #     method 2
    #     user = request.user
    #     if user.is_authenticated:
    #         # 如果是登录用户展示用户中心界面
    #         return render(request, 'user_center_info.html')

    #     else:
    #         # 如果是未登录用户就重定向到login
    #         # return redirect('/login/')
    #         return redirect('/login/?next=/info/')

    # method 3
    def get(self, request):
        return render(request, 'user_center_info.html')


class EmailView(LoginRequiredMixin, View):
    # 分析前端传入数据的数据格式,类型，决定数据的接收方法/GET/POST/PUT
    def put(self, request):
        # 向用户添加邮箱 ,以下代码会重复执行，影响程序性能
        # # json_str_bytes = request.body # request.body返回bytes类型
        # # json_str = json_str_bytes.decode() # 将bytes类型 转为json字符串
        # # data = json.loads(json_str) # 将json字符串转换为字典
        # # email = data.get('email') # 将字典里存储的email 获取到
        # # if email is None:
        # #     return http.HttpResponseForbidden('请填写邮箱后重试')
        # # # 校验email
        # # if  not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        # #     return http.HttpResponseForbidden('请输入正确的邮箱')
        # user = request.user
        # user.email = email
        # user.save()
        user = request.user  # 获取user用户
        # 优化设置用户邮箱
        # 判断当前user用户的email是否为空，从mysql中查询。。
        if not user.email:
            json_str_bytes = request.body
            json_str = json_str_bytes.decode()
            data = json.loads(json_str)
            new_email = data.get('email')
            # 判断前端 input 标签传入的 email是否为空
            if new_email is None:
                return http.HttpResponseForbidden('请填写邮箱后重试')
            # 校验email
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', new_email):
                return http.HttpResponseForbidden('请输入正确的邮箱')
            # 校验通过后，保存user用户的邮箱
            user.email = new_email
            user.save()
            # 用户邮箱保存后，要进行判断用户邮箱 是否验证(用户能否通过当前email收发邮件)
            # 使用django内部发送邮件的模块。不同项目 需要更改发送邮件相关 的配置
            '''
            send_mail(subject='邮箱主题', message='邮件普通', from_email='发件人',
                      recipient_list='收件人列表',html_message='邮件超文本内容')
            '''
            # 可以使用celery  异步执行发送邮箱的功能
            # subject = "美多商城邮箱验证"
            # html_message = '<p>尊敬的用户您好！</p>' \
            #                '<p>感谢您使用美多商城。</p>' \
            #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' % new_email
            # send_mail(subject=subject,
            #           message='',
            #           from_email=settings.EMAIL_FROM,
            #           recipient_list=[new_email],
            #           html_message=html_message)

        verify_url = generate_email_verify_url(user)
        send_verify_email(to_email=user.email, verify_url=verify_url)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class EmailVerifyView(View):
    def get(self, request):
        token = request.GET.get('token')
        if token is None:
            return http.HttpResponseForbidden('缺少必传参数')
        user = check_out_user_email(token=token)
        if user is None:
            return http.HttpResponseForbidden('邮件激活失败')
        user.email_active = True
        user.save()
        return redirect('/info/')


class AddressView(LoginRequiredView):

    def get(self,request):
        return render(request,'user_center_site.html')


class AddressCreateView(LoginRequiredView):
    # 前端使用post发起的请求
    def post(self,request):
        # 接收数据，前端传入了一个json数据
        json_data = json.loads(request.body.decode())
        # html 必填
        title =json_data.get('title')
        receiver =json_data.get('receiver')
        province_id =json_data.get('province_id')
        city_id =json_data.get('city_id')
        district_id =json_data.get('district_id')
        place =json_data.get('place')
        mobile =json_data.get('mobile')
        #  选填
        tel =json_data.get('tel')
        email =json_data.get('email')
        # 校验数据
        if not all([title,receiver,province_id,city_id,district_id,place]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('Error Mobile')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('Error Tel')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('Error Email')
        try:
            address = Address.objects.create(
                user=request.user,
                title=title,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            # 判断当前地址是否是用户的默认地址
            # if not request.user.default_address:
            #     request.user.default_address = address
            #     request.user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('Address Create Failed')
        address_dict={
                        "id":address.id,
                        "title":address.title,
                        "receiver":address.receiver,
                        "province":address.province.name,
                        "city":address.city.name,
                        "district":address.district.name,
                        "place":address.place,
                        "mobile":address.mobile,
                        "tel":address.tel,
                        "email":address.email}
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','address':address_dict})