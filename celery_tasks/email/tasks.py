from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app

@celery_app.task(bind=True,name='send_verify_email',retry_backopff=3)
def send_verify_email(self,to_email,verify_url,message):
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！<p>' \
            '<p>感谢您使用美多商城。 <p> '\
            '<p>您的邮箱为：%s。请点击此链接激活您的邮箱：<p> ' \
            '<p>  %s </p>' % (to_email, verify_url)
    try:
        send_mail(subject=subject,message=message,from_email=settings.EMAIL_HOST_USER,recipient_list=[to_email],html_message=html_message)
    except Exception as e:
        # 设置最多试错3次
        raise self.retry(exc=e,max_retries=3)

