from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from datetime import date
from users.models import Users
from orders.models import OrderInfo
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from datetime import timedelta
from goods.models import GoodsVisitCount,GoodsCategory
from django.core.serializers.json import DjangoJSONEncoder

class UserCountView(APIView):
    #权限指定
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    '''用户总量统计'''
    def get(self, request):
        #获取日期
        now_date=date.today()
        #获取用户总量
        total_count= Users.objects.all().count()
        #返回结果
        return Response(
            {
                'date':now_date,
                'count':total_count
            }
        )

class UserIncreaseView(APIView):
    #权限指定
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    '''用户新增统计'''
    def get(self, request):
        #获取日期
        now_date=date.today()
        #获取新增用户
        count= Users.objects.filter(date_joined__gte=now_date).count()
        #返回结果
        return Response(
            {
                'date':now_date,
                'count':count
            }
        )

class UserActiveView(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    '''用户日活统计'''
    def get(self, request):
        # 获取日期
        now_date = date.today()
        # 获取日活用户
        count = Users.objects.filter(last_login__gte=now_date).count()
        # 返回结果
        return Response(
            {
                'date': now_date,
                'active_count': count
            }
        )


class UserOrderView(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    '''日分类统计'''
    def get(self, request):
        # 获取日期
        now_date = date.today()
        # 获取下单用户
        # orders= OrderInfo.objects.filter(create_time__gte=now_date)
        # user_count = orders.values('user').distinct().count()
        #或者使用关联过滤查询： 主键模型.filter（外键模型名称小写+外键模型查询字段+条件)
        user_count = Users.objects.filter(orderinfo__create_time__gte=now_date).count()
        # 返回结果
        return Response(
            {
                'date': now_date,
                'order_count':  user_count
            }
        )


class UserMonthView(APIView):
    # 权限指定
    # permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    '''最近一个月内的新增用户统计'''
    def get(self, request):
        # 获取日期
        now_date = date.today()
        #新增用户统计，统计当前日期-30天之间所有新增的用户
        before_month_date=now_date-timedelta(days=30)

        date_list=[]
        for i in range(31):
            b_date=before_month_date+timedelta(days=i)
            n_date=b_date+timedelta(days=i+1)

            count = Users.objects.filter(date_joined__gte=b_date, date_joined__lt=n_date).count()
            date_list.append({b_date.isoformat(): count})
        # 返回结果
        return Response(
            {
                'count': date_list
            }
        )




class GoodsVistView(APIView):

    # 权限指定
    # permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    '''当日浏览商品统计'''
    def get(self, request):
        # 获取日期
        now_date = date.today()

        category_list=[]
        category_set = GoodsVisitCount.objects.filter(date__gte=now_date)
        for categorys in category_set:
            category_list.append(categorys.category_id)

        goods_list = []
        for category in category_list:
            count= GoodsVisitCount.objects.get(date__gte=now_date,category_id=category).counts
            category_second = GoodsCategory.objects.get(id=category).parent_id
            # category_first = GoodsCategory.objects.get(id=category_second).parent_id
            # category_name = GoodsCategory.objects.get(id=category_first).name
            category_name = GoodsCategory.objects.get(id=category_second).name
            goods_list.append({category_name: count}) #用的二级分类结果

        print(goods_list)

        # 返回结果
        return Response(
            {
                'count': goods_list
            }
        )
