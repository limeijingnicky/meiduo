from django.shortcuts import render,redirect
from django.views import View
from areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache
from django.http import HttpResponse,JsonResponse
from rest_framework_jwt.views import obtain_jwt_token
from users.models import Users


class LoginAdminsView(View):
    def get(self,request):
        return render(request,"login_admins.html")

    def post(self,request):
        ##校验数据库中的username和pass是否正确,以及是否是超级管理员身份
        username = request.POST.get("username")
        password = request.POST.get("password")

        print(username)
        print(password)

        user= Users.objects.get(username=username)
        is_super = user.is_superuser
        if user and is_super==1:
            if user.check_password(password):
                return render(request,'login_admins.html',{'loginmsg':{'code':202,'errmsg':'管理员成功登录'}})
            else:
                return render(request,'login_admins.html',{'loginmsg':{'code': 411, 'errmsg': '管理员密码错误'}})
        else:
            return render (request,'login_admins.html',{'loginmsg':{'code': 412, 'errmsg': '不是管理员'}})


