import http
from django.shortcuts import render
from django.views import View
from verifications.captch import imgcode
from django.http import HttpResponse,JsonResponse,HttpResponseForbidden
from django_redis import get_redis_connection
from io import BytesIO
import base64
import random
import logging
from celery_tasks.sms.tasks import send_sms_code


#创建日志输出器
logger = logging.getLogger('aaa')


class ImageCodeView(View):
    #图形验证码
    def get(self,request,uuid):
        # uuid,标识验证码属于哪个用户
        ##生成图形验证码和文字
        img,code=imgcode.check_code()


        #将图像保存为png的字节流
        img_bytes_io = BytesIO()
        img.save(img_bytes_io, format="PNG")

        #将内容转为字符串
        img_bytes = img_bytes_io.getvalue()

        # 保存图形验证码到redis数据库
        redis_con=get_redis_connection('verify_code') #设置一个redis对象
        redis_con.set("{0}".format(uuid),code,ex=300) ##将value关联到key，key，expires，value(将uuid作为key和验证码文本关联，并加上300s时间)
        redis_con.set("{0}_image_code".format(uuid),img_bytes,ex=300)

        # 从Redis中获取图像数据
        uuid = uuid
        redis_con = get_redis_connection('verify_code')
        img_bytes = redis_con.get("{0}_image_code".format(uuid))

        # 将图像数据编码为base64字符串
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # # 响应图形验证码
        context = {'img_base64':img_base64}
        # print(context['img_base64'])
        # print(type(context['img_base64']))
        # return render(request,'register.html',context)
        return JsonResponse(context)

class SMSCodeView(View):
    ##短信验证码
    def get(self,request,mobile):
        ##接收参数
        image_code_client=request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        ##校验参数，数据是否都有值
        if not all([image_code_client,uuid]):
            return HttpResponseForbidden('缺少必要参数')

        ##判断用户是否频繁发送短信验证
        redis_con = get_redis_connection('verify_code')
        sms_code_flag = redis_con.get("{0}_send_flag".format(mobile))

        if sms_code_flag:
            return JsonResponse({'code':'4004','errmsg':'已发送短信验证码'})

        ##提取图形验证码（删除图形验证码），对比图形验证码
        #提取图形验证码
        image_code_server=redis_con.get(uuid)
        if image_code_server is None:
            return JsonResponse({'code':'4001','errmsg':'图形验证码已失效'})
        #删除图形验证码
        redis_con.delete(uuid+'_image_code')
        #将redis里的bytes类型转为字符串类型
        image_code_server=image_code_server.decode()

        redis_con.delete(uuid)

        #对比两个图形验证码是否一致(转小写)
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({'code':'4001','errmsg':'输入图形验证码有误'})


        ##生成短信验证码，保存短信验证码，发送短信验证码
        # 随机生成六位数的短信验证码
        sms_code = 0
        for i in range(6):
            a=random.randint(0,10)
            sms_code=sms_code+a*pow(10,i)

        ##将sms_code写到日志里
        logger.info(sms_code)

        #保存短信验证码到数据库redis
        redis_con = get_redis_connection('verify_code')  # 设置一个redis对象
        redis_con.set(mobile, sms_code, ex=60)  ##将value关联到key，key，expires，value(将uuid作为key和验证码文本关联，并加上300s时间)

        #保存一个sent_flag
        redis_con = get_redis_connection('verify_code')  # 设置一个redis对象
        redis_con.set(mobile+"_send_flag", 1, ex=60)


        #优化 使用pipeline执行redis，同时执行多个任务，提高服务器的效率
        # pl=redis_con.pipeline()
        # pl.set(mobile, sms_code, ex=60)
        # pl.set(mobile+"_send_flag", 1, ex=60)
        #
        # pl.execute()


        # 发送短信验证码
        # send_template_sms(mobile,[sms_code],5),1) #调用固定方法和参数

        # 优化 使用celery进行异步执行
        # send_sms_code.delay(mobile,sms_code)
        # print('this is celery, it is ok')

        ##响应结果
        return JsonResponse({'code':'0','errmsg':'短信发送成功'})


class SMSCheckView(View):
    #图形验证码
    def get(self,request,mobile):

        # 提取图形验证码
        redis_con = get_redis_connection('verify_code')
        sms_code_server = redis_con.get(mobile)
        if sms_code_server is None:
            return JsonResponse({'code': '4002', 'errmsg': '请输入短信验证码'})

        ##响应结果
        return JsonResponse({'code': '1', 'errmsg': sms_code_server.decode()})
