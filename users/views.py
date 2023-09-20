from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
import re
from users.models import Users
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login


##设计子接口逻辑，
# 包括请求方法，get post put delete
# 请求地址，url
# 请求参数，路径参数，查询字符串，表单，json
# 响应数据，响应数据 html json


class UsernameCountView(View):
    def get(self,request,username):

        counts = Users.objects.filter(username=username).count()
        if counts == 0:
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': counts})

        else:
            return JsonResponse({'code': 404, 'errmsg': 'error with repeat of id', 'count': counts})

class MobileCountView(View):
    def get(self,request,mobile):
        counts = Users.objects.filter(mobile=mobile).count()
        if counts == 0:
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': counts})

        else:
            return JsonResponse({'code': 404, 'errmsg': 'error with repeat of mobile', 'count': counts})






class RegisterView(View):
    #用户注册
    def get(self,request):
        # return HttpResponse('it is ok')
        return render(request,'register.html')


    def post(self,request):
        ##接收参数,表单数据用POST接收，非表单JSON用body收，然后非序列化

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')



        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([username, password,password2,mobile,allow,uuid]):
            return HttpResponseForbidden('缺少必填项')

        # 用户名是否为5-20个字符；
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')

        # 密码是否为8-20个字符；
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20个字符的密码')

        # 判断两次输入密码是否一致；
        if password != password2:
            return HttpResponseForbidden('两次输入的密码不一致')

        # 手机号码是否合法；
        if not re.match(r'^1[0-9]\d{9}$',mobile):
            return HttpResponseForbidden('请输入正确的手机号码')
        # 是否勾选了协议
        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议')



        ##保存注册数据 (核心代码)
        ##利用models里的用户表单模型进行数据存储,数据库储存错误就重定向到注册页面


        try: #返回一个对象
            Users.objects.create_user(username=username,password=password,mobile=mobile)

        except DatabaseError :
            return render(request,'register.html',{'register_error': '注册失败'})


        ##用户登录状态保持,将用户的信息保存在session里
        # login(request,user)



        ##响应结果:重定向到首页
        # return render(request,template_name='index')

        # return redirect(reverse('content : index')) ##反向解析后得到路由
        return redirect('/')



# python manage.py runserver
