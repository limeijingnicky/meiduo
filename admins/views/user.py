from rest_framework.views import APIView
from django.views import View
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from datetime import date
from users.models import Users
from orders.models import OrderInfo
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from datetime import timedelta
from goods.models import GoodsVisitCount,GoodsCategory
from django.core.paginator import Paginator,EmptyPage
from django.http import HttpResponseNotFound

class UsersView(View):
    # 权限认证
    # permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def get(self,request,keyword,page_num):
        # print(keyword)
        user_list = []
        # 当不存在查询参数时，即返回所有用户信息
        if not keyword:
            users = Users.objects.filter(is_staff=False)
        else:
            users = Users.objects.filter(username=keyword, is_staff=False)
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
