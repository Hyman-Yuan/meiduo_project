from celery_tasks.sms import constant
from celery_tasks.main import celery_cli
from celery_tasks.sms.yuntongxun.sms import CCP


# name: 给当前异步任务取别名
@celery_cli.task(name='ccp_send_sms_code')
def ccp_send_sms_code(mobile,sms_verify_code):

    #CCP.send_template_sms(to=接收验证码的手机号, datas=[后端随机生成的验证码,验证码有效时间 ], temp_id=1)
    CCP.send_template_sms(to=mobile, datas=[sms_verify_code,constant.SMS_CODE_EXPIRETIME // 60 ], temp_id=1)