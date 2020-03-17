from celery import Celery
import os

# 在当前程序系统环境中添加django配置文件模板,
# 如果当前celery 中有函数或者方法使用了django的配置文件，则必须加
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 创建celery实例
# 1.创建celery客户端对象 Celery第一个位置参数是当前任务的别名
celery_cli = Celery('meiduo_mall')

# 加载celery配置
# 2.载入celery的配置信息,指定任务队列的存储位置,传入当前celery的配置文件作为参数
celery_cli.config_from_object('celery_tasks.config')

# 自动注册celery任务
# 3.给当前celery的 任务列表 添加任务,[]列表里的参数,是任务的导包路径

celery_cli.autodiscover_tasks([
    'celery_tasks.sms',
])