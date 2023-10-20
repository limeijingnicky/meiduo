# 开发环境的配置文件

"""
Django settings for meiduo project.

Generated by 'django-admin startproject' using Django 3.2.18.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import logging


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--o=9vwhxwyag3y5%*f0fdgi)!%_0tyvu@=g=xqa#)7=4+f2b#f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig', ##用户注册页面
    'contents.apps.ContentsConfig', ##首页广告页面
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',#省市区联动

    # 注册过滤模块
    'django_filters',

    # 注册restframework
    # 'rest_framework',

]

#
# ##对全局的drf框架进行认证的设置
# REST_FRAMEWORK = {
#     ##权限设置
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework.authentication.BasicAuthentication',  ##基本认证
#         'rest_framework.authentication.SessionAuthentication',  ##session认证
#     ),
#     ##流量设置，用户分类和频次
#     'DEFAULT_THROTTLE_CLASSES': (
#         # 'rest_framework.throttling.AnonRateThrottle',
#         # 'rest_framework.throttling.UserRateThrottle',
#
#         'rest_framework.throttling.ScopedRateThrottle',  # 对不同视图限制访问次数
#     ),
#     'DEFAULT_THROTTLE_RATES': {
#         # 'anon': '1/day', ##匿名用户
#         # 'user': '200/day', ##登录用户 second, minute,hour,day
#
#         # 'bookview': '100000/day'
#     },
#
#     # 过滤filtering
#     'DEFAULT_FILTER_BACKENDS': [
#         'django_filters.rest_framework.DjangoFilterBackend'],
#
#     # 分页设置
#     'DEFAULT_PAGINGATION_CLASS': (
#         'django_filters.rest_framework.pagination.PageNumberPagination'),
#     'PAGE_SIZE': 10,  # 设置每页数目
#
#     ##更改异常捕捉方法
#     # 'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler', 默认的方法
#     'EXCEPTION_HANDLER': 'exceptions.exception_handler',
#
#     # api文档设置
#     'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
# }

##中间键用来监听 请求处理前  和 响应
##在请求处理之前从上而下执行，请求处理之后即响应是从下往上执行
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # ##注册中间键
    # 'middleware.my_middleware',
]

# 工程配置的路由文件入口
ROOT_URLCONF = 'meiduo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'jinja2_env.environment',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo.wsgi.application'

# Database 换成需要的数据库种类
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'POST': '3306',
        'USER': 'root',
        'PASSWORD': '1234',
        'NAME': 'meiduo'
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# 静态文件访问路由前缀
STATIC_URL = '/static/'
# 配置静态文件加载存储目录
STATICFILES_DIRS = [

    os.path.join(BASE_DIR, 'static'),

]

##设置session的存储，使用redis存储，是一种高速存取的数据库，适用于键值对形式数据
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": { #验证码
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"  ##普通缓存在default里的0，session缓存在session里的1 完成分库

##admin 管理网页里上传的图片储存的位置
MEDIA_ROOT = os.path.join(BASE_DIR, 'static /media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


##配置工程日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
     'verbose': {
        'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
    },
     'simple': {
        'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
    }
},
    'filters': {  # 对日志进行过滤
     'require_debug_true': {  # django在debug模式下才输出日志
        '()': 'django.utils.log.RequireDebugTrue',
    },
},
    'handlers': {  # 日志处理方法
     'console': {  # 向终端中辅出日志
        'level': 'INFO',
        'filters': ['require_debug_true'],
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
     'file': {  # 向文件中输出日志
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': 'C:/Users/KDG/meiduo/logs/meiduo.log',  # 日志文件的位置
        'maxBytes': 300*1024*1024,
        'backupCount': 10,
        'formatter': 'verbose',
    }
},
    'loggers': {  # 日志器____
     'meiduo': {  # 定义了一个名为meiduo的日志器
        'handlers': ['console','file'], # 可以同时向终据与文件中输出日志
        'propagate': True,  # 是否能续传迷日志信息
        'level': 'INFO',  # 日志器接收的最低日志级别
    },
},
}

##指定自定义的用户模型类，子应用.模型名称
AUTH_USER_MODEL = 'users.Users'


##指定自定义用户认证后端
AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileBackend']


##配置未登录用户的重定向页面
LOGIN_URL='/login'


# Q0登录的配置参数,申请应用的时候生成
QO_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
Q0_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'


#配置email参数
EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'#导入邮件模块
EMAIL_HOST='smtp.gmail.com'#发邮件主机
EMAIL_PORT=587 #发邮件端口
EMAIL_USE_TLS = True  # 使用 TLS 安全连接

EMAIL_HOST_USER='limeijingnicky@gmail.com'#授权的邮箱
EMAIL_HOST_PASSWORD='kayqyillldnqgxqh'#邮箱授权时获得的密码,非注册登录密码
EMAIL_FROM ='美多商城' #发件人抬头

EMAIL_VERIFY_URL='http://127.0.0.1:8000/verification/'




