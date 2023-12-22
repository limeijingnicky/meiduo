from rest_framework.views import APIView
from django.views import View
from django.shortcuts import render,redirect
from rest_framework.permissions import IsAdminUser
from datetime import date
from users.models import Users
from orders.models import OrderInfo
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from datetime import timedelta
from goods.models import GoodsVisitCount,GoodsCategory
from django.core.paginator import Paginator,EmptyPage
from django.http import HttpResponseNotFound,HttpResponseForbidden,HttpResponse,JsonResponse
import re
from django.db import DatabaseError
import json
class UsersView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def get(self,request,keyword,page_num):
        # print(keyword)
        user_list = []
        # 当不存在查询参数时，即返回所有用户信息
        if not keyword:
            users = Users.objects.filter(is_staff=False)
        else:
            users = Users.objects.filter(username__icontains=keyword, is_staff=False)
            if not users.exists():
                return render(request, 'user_admins.html', {'users': user_list})

        # for user in users:
        #     dic={
        #         "id": user.id,
        #         "name": user.username,
        #         "mobile": user.mobile if user.mobile else " ",
        #         "email": user.email if user.email else " "
        #     }
        #     user_list.append(dic)
        #
        # return render(request, 'user_admins.html', {'users': user_list})

        paginator= Paginator(users,2)
        total_page = paginator.num_pages

        #获取当前页的数据和总页数
        # page_dict={}
        # for i in range(total_page):
        try:
            page_users=paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('当前页面不存在')

        user_list=[]
        for user in page_users:
            dic={
                    "id": user.id,
                    "name": user.username,
                    "mobile": user.mobile if user.mobile else " ",
                    "email": user.email if user.email else " "
                }
            user_list.append(dic)

            # page_dict[str(i)]=user_list

        context = {
            'page_users': user_list,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request,'user_admins.html',context=context)

class UserAddView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]
    def post(self,request):

        data = json.loads(request.body)
        username = data.get('userr')
        password = data.get('password')
        email = data.get('email')
        mobile = data.get('mobile')

        # print(username)
        # print(password)
        # print(mobile)
        # print(email)


        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([username, password]):
            return HttpResponseForbidden('缺少必填项')

        # 用户名是否为5-20个字符；
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')

        # 密码是否为8-20个字符；
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20个字符的密码')

        # 手机号码是否合法；
        if not re.match(r'^1\d{10}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号码')

        #电子邮箱是否合法；
        if not re.match(r'^\w+@\w+\.\w+$', email):
            return HttpResponseForbidden('email格式不正确')

        try:  # 返回一个对象
            user = Users.objects.create_user(username=username, password=password, mobile=mobile,email=email)
            return JsonResponse({'code': 'ok','register_error':f'添加ID{user.id} 用户 成功'})

        except DatabaseError:
            return JsonResponse({'code': 'fail','register_error': '添加用户失败'})



