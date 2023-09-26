#定义任务
from celery_tasks.main import celery_app


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code):
    # 发送短信验证码
    # send_ret=send_template_sms(mobile,[sms_code],5),1) #调用固定方法和参数
    # return send_ret
    pass