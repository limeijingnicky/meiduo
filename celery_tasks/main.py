##celery入口文件
from celery import Celery

#创建Celery实例,生产者消费者模式
celery_app=Celery('meiduo')

#加载配置
celery_app.config_from_object('celery_tasks.config')

#注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])


# celery -A celery_tasks.main worker --loglevel=info     celery命令行

