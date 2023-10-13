##celery入口文件
from celery import Celery
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE','meiduo.settings')

#创建Celery实例,生产者消费者模式
celery_app=Celery('meiduo')

#加载配置
celery_app.config_from_object('celery_tasks.config')

#注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])


# celery -A celery_tasks.main worker -l info -P eventlet     celery命令行

# celery -A celery_tasks.main worker -l info -P eventlet --concurrency 20   开多线程

