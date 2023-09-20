from django.shortcuts import render
from django.views import View
from verifications.captch import imgcode
from django.http import HttpResponse,JsonResponse
from django_redis import get_redis_connection
from io import BytesIO
import base64

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

