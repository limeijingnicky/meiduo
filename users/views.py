from django.shortcuts import render
from django.views import View
from django.http import HttpResponse


##设计子接口逻辑，
# 包括请求方法，get post put delete
# 请求地址，url
# 请求参数，路径参数，查询字符串，表单，json
# 响应数据，响应数据 html json


# Create your views here.
class RegisterView(View):
    #用户注册
    def get(self,request):
        # return HttpResponse('it is ok')
        return render(request,'register.html')

    def post(self,request):
        ##接收参数,表单数据用POST接收，非表单JSON用body收，然后非序列化
        value=request.POST.get('key')


        ##校验参数


        ##保存注册数据


        return

