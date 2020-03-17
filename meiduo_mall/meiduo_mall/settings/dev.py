"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os,sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0,os.path.join(BASE_DIR,'apps'))


'''['/home/python/Desktop/meiduo_project/meiduo_mall/meiduo_mall/apps',
    '/home/python/Desktop/meiduo_project/meiduo_mall',
    '/home/python/Desktop/meiduo_project/meiduo_mall', 
    '/snap/pycharm-professional/183/plugins/python/helpers/pycharm_display',
    '/home/python/.virtualenvs/meiduo_project/lib/python36.zip',
    '/home/python/.virtualenvs/meiduo_project/lib/python3.6',
    '/home/python/.virtualenvs/meiduo_project/lib/python3.6/lib-dynload',
    '/usr/lib/python3.6', 
    '/home/python/.virtualenvs/meiduo_project/lib/python3.6/site-packages', 
    '/snap/pycharm-professional/183/plugins/python/helpers/pycharm_matplotlib_backend']
/home/python/Desktop/meiduo_project/meiduo_mall/meiduo_mall
['/home/python/Desktop/meiduo_project/meiduo_mall/meiduo_mall/apps', '/home/'''

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'cx05qh%+zf7m=cut&i_n@)_!64e6x@y5uz&tt!0zy=l-z3rjuu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.meiduo.site','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user.apps.UserConfig',
    'oauth.apps.OauthConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'meiduo_mall.utils.jinja2_env.jinja2_environment',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'meiduo_mall',
        'HOST': 'localhost',
        'PORT': 3306,
        'USER': 'meiduo_user',
        'PASSWORD': 'meiduo_user',

    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = 'en-us'
#
# TIME_ZONE = 'UTC'
# alert the language and time in system
LANGUAGE_CODE = 'zh-hans' # 使用中国语言
TIME_ZONE = 'Asia/Shanghai' # 使用中国上海时间

USE_I18N = True

USE_L10N = True

USE_TZ = True

CACHES = {
    'default':{
        'BACKEND':'django_redis.cache.RedisCache',
        'LOCATION':'redis://127.0.0.1:6379/0',
        'OPTIONS':{
            'CLIENT_CLASS':'django_redis.client.DefaultClient'
        }
    },
    'session':{
        'BACKEND':'django_redis.cache.RedisCache',
        'LOCATION':'redis://127.0.0.1:6379/1',
        'OPTIONS':{
            'CLIENT_CLASS':'django_redis.client.DefaultClient'
        }
    },
    'verify_codes':{
        'BACKEND':'django_redis.cache.RedisCache',
        'LOCATION':'redis://127.0.0.1:6379/2',
        'OPTIONS':{
            'CLIENT_CLASS':'django_redis.client.DefaultClient'
        }
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_CACHE_ALIAS = 'session'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static')
]

# 配置项目日志文件

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# 修改Django用户认证模型类
AUTH_USER_MODEL = 'user.User'

# AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
# 指定Django认证后端类 AccountAuthBackend(自定义认证后端类)
AUTHENTICATION_BACKENDS = ['user.utils.AccountAuthBackend']

# 判断登录时,LoginRequiredMixin的配置项,
# 默认 LOGIN_URL = '/accounts/login/'
LOGIN_URL = '/login/'

# QQ_login config patterns
QQ_CLIENT_ID = '101518219'     # APPid
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'  # APPkey
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'   # 回调地址

# 邮件配置
# 系统配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_PORT = 25  # 发邮件端口

# 当前项目的配置
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_HOST_USER = '13550585028@163.com'  # 授权的邮箱
#  POP3/IMAP/SMTP
EMAIL_HOST_PASSWORD = 'UJKNPTNUEKXTPSKN'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<13550585028@163.com>'  # 发件人抬头

# EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
# EMAIL_HOST_USER = 'itcast99@163.com'  # 授权的邮箱
# EMAIL_HOST_PASSWORD = 'python99'  # 邮箱授权时获得的密码，非注册登录密码
# EMAIL_FROM = '美多商城<itcast99@163.com>'  # 发件人抬头

# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'