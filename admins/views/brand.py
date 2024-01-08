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
from goods.models import Brand
from django.core.paginator import Paginator,EmptyPage
from django.http import HttpResponseNotFound,HttpResponseForbidden,HttpResponse,JsonResponse
import re
from django.db import DatabaseError
from goods.models import SPU,SPUSpecification
import json
from views.spec import chinese_len
from django.core.cache import cache
import logging

#创建日志输出
logger=logging.getLogger('meiduo')


class BrandView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def get(self, request, page_num, keyword):
        keyword = request.GET.get('keyword')
        page_num = page_num

        brans= []
        # 当不存在查询参数时，即返回所有规格信息
        if not keyword:
            # 查询数据库中的对象
            brands = Brand.objects.all()

        else:
            brands = Brand.objects.filter(name__contains=keyword)
            if not brands:
                return render(request, 'brands_admins.html', {'page_brands': brans})

        # 根据模型之间的外键进行关联查询
        brandss = []
        for brand in brands:
            brandss.append(
                {
                    'brandid': brand.id,
                    'brandname': brand.name,
                    'brandlogo': brand.logo,
                    'brandfirstletter': brand.first_letter
                }
            )

        paginator = Paginator(brandss, 2)
        total_page = paginator.num_pages

        try:
            bs = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('当前页面不存在')

        context = {
            'page_brands': bs,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request, 'specs_admins.html', context=context)

class BrandGetView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]
    def get(self,request):
        brand_id = request.GET.get('brand_id')

        if not brand_id:
            # 获取缓存数据
            brand_model_list = cache.get('brand_model_list')

            if not brand_model_list:
                brand_models = Brand.objects.all()
                brand_model_list = []
                for brand_model in brand_models:
                    p = {
                        'id': brand_model.id,
                        'name': brand_model.name
                    }
                    brand_model_list.append(p)
                # 将自动加载的数据，进行缓存
                cache.set(' brand_model_list',  brand_model_list, 3600)
                return JsonResponse({'code': 0, 'errmsg': 'ok', 'brand': brand_model_list})
            else:
                return JsonResponse({'code': 0, 'errmsg': 'ok', 'brand': brand_model_list})
        else:
            brand_models = Brand.objects.filter(id=brand_id)
            if brand_models:
                brand_model_list = []
                for brand_model in brand_models:
                    p={
                        'id': brand_model.id,
                        'name': brand_model.name
                    }
                    brand_model_list.append(p)
                return JsonResponse({'code': 0, 'errmsg': 'ok', 'brand': brand_model_list})
            else:
                return JsonResponse({'code': 419, 'errmsg': '当前品牌不存在'})
