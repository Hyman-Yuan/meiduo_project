from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
from random import randint


from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constant


import logging
logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码
    uuid 前端请求 通过正则组 提取的"""
    def get(self,request,uuid):
        """
        1. 调用图形验证码SDK 生成图形验证码数据
            captcha.generate_captcha()
                return name, text, out.getvalue()
                    name: 随机唯一标识
                    text: 图形验证码字符串 内容
                    out.getvalue(): 图形验证码图片  (bytes类型)
        """
        # captcha:第三方工具,用于生成图形验证码
        name,image_str,image_code_bytes = captcha.generate_captcha()
        #  redis连接对象,
        #  before storing the data in the cache,must config the cache.
        #  get_redis_connection(alias='default', write=True)
        # 配置当前 需要使用的redis数据库,默认使用CACHE中'default'数据库
        redis_cli = get_redis_connection('verify_codes')
        # redis_cli = get_redis_connection()
        # redis_cli.setex(key, 过期时间, value)
        # 存储图形验证码目的是为了后面发短信时,比对图形验证码是否填写正确
        redis_cli.setex(uuid, 300, image_str)
        return http.HttpResponse(image_code_bytes, content_type='image/jpeg')

        # ImageCodeView 核心代码
        # name, image_str, image_code_bytes = captcha.generate_captcha()
        # redis_cli = get_redis_connection('verify_codes')
        # redis_cli.setex(uuid, 300, image_str)
        # return http.HttpResponse(image_code_bytes, content_type='image/jpeg')




# // 向后端接口发送请求，让后端发送短信验证码
#    var url = this.host + '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
class SMSCodeView(View):
    """短信验证码"""
    def get(self,request, mobile):
        # 接收参数
        query_dict = request.GET
        image_code_client = query_dict.get('image_code')
        uuid = query_dict.get('uuid')

        # 创建连接到redis的对象
        redis_obj = get_redis_connection('verify_codes')
        # 1 首先校验当前手机号 是否 已经发送短信,如若发送,redis中会有记录
        mobile_is_use =  redis_obj.get(mobile)
        # 如果手机号已经使用,则mobile_is_use 返回非空的结果,表示条件成立,执行if语句内部代码块
        if mobile_is_use:
            return http.JsonResponse({'code':RETCODE.THROTTLINGERR,'errmsg':"访问过于频繁"})
        # 校验参数
        if not all([image_code_client,uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 提取图形验证码 from redis
        # redis_cli.setex(uuid, 300, image_str)  图形验证码的存储 过程
        image_verify_code = redis_obj.get(uuid)   # (bytes类型)
        redis_obj.delete(uuid)                    # 获取到图形验证码后,删除redis中的图形验证码.避免图形验证码重复使用
        if image_verify_code is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已过期'})
        # 对比图形验证码
        image_code_server = image_verify_code.decode()
        if image_code_client.upper() != image_code_server.upper():
            return http.HttpResponseForbidden({'code':RETCODE.IMAGECODEERR,'errmsg':'图形验证码填写错误'})
        # 生成短信验证码：生成6位数验证码
        sms_verify_code = "%06d" % randint(0,999999)
        print(sms_verify_code)
        logger.info(sms_verify_code)

        # # 保存短信验证码,constant.SMS_CODE_EXPIRETIME 使用常量替换代码中的数字
        # redis_obj.setex('sms_%s' % mobile, constant.SMS_CODE_EXPIRETIME,sms_verify_code)
        # # 在redis中 标识手机号已经使用
        # redis_obj.setex(mobile, constant.MOBILE_EXPIRETIME, constant.MOBILE_FREQUENCY)
        """使用管道命令处理 redis 请求,节约频繁访问redis数据库 所消耗的时间"""
        # 创建管道对象,使用管道对象 向redis 中写入数据
        pl = redis_obj.pipeline()
        # # 发送短信验证码
        pl.setex('sms_%s' % mobile, constant.SMS_CODE_EXPIRETIME, sms_verify_code)
        pl.setex(mobile, constant.MOBILE_EXPIRETIME, constant.MOBILE_FREQUENCY)


        CCP.send_template_sms(to=mobile, datas=[sms_verify_code,constant.SMS_CODE_EXPIRETIME // 60 ], temp_id=1)
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

