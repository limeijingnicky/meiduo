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
from goods.models import SPU,SPUSpecification
import json
from views.spec import chinese_len


class SpusView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def get(self,request,page_num,keyword):
        keyword=request.GET.get('keyword')
        page_num=page_num
        # print(page_num)
        # print(keyword)

        spuid=[]
         # 当不存在查询参数时，即返回所有规格信息
        if not keyword:
            #查询数据库中的spu对象
            spus = SPU.objects.all()

        else:
            # print(keyword)
            spus = SPU.objects.filter(name__contains=keyword)
            if not spus:
                return render(request,'spus_admins.html', {'page_spus': spuid})

        #根据模型之间的外键进行关联查询
        spuu=[]
        for spu in spus:
            spuu.append(
                {
                    'spuid' : spu.id,
                    'spuname' : spu.name,
                    'spudetail' : spu.desc_detail,
                    'spupack': spu.desc_pack,
                    'spuservice': spu.desc_service
                }
            )
        print(spuu)

        paginator = Paginator(spuu, 2)
        total_page = paginator.num_pages

        try:
            spuss = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('当前页面不存在')

        context = {
            'page_spus': spuss,
            'total_page': total_page,
            'page_num': page_num,
        }
        # print(context)
        # 查询一个作者的所有书籍
        # author_instance = Author.objects.get(id=1)
        # books = author_instance.books.all()（books为Book模型中的关联字段，否则默认为book_set）
        return render(request,'spus_admins.html',context=context)


class SpusAddView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def post(self,request):

        data = json.loads(request.body)
        spuname = data.get('spuname')
        cl1 = data.get('cl1')
        cl2 = data.get('cl2')
        cl3 = data.get('cl3')
        brand = data.get('brand')

        print(data)

        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([spuname, cl1, cl2, cl3,brand]):
            return HttpResponseForbidden('缺少必填项')

        if chinese_len(spuname)>50:
            return HttpResponseForbidden('请输入1-50个字符的SPU商品名称')

        if chinese_len(spuname) > 20:
            return HttpResponseForbidden('请输入1-20个字符的品牌名称')

        #SPU商品名不能存在
        spu =SPU.objects.filter(name=spuname)
        if not spu :
            try:  # 返回一个对象
                se=SPU.objects.create(name=spuname,brand_id=brand,category1_id=cl1,category2_id=cl2,category3_id=cl3)
                return JsonResponse({'code': 'ok','register_error':f'添加{spuname} SPU商品 成功'})

            except DatabaseError:
                return JsonResponse({'code': 'fail','register_error': '添加SPU商品失败'})
        else:
            return JsonResponse({'code': 'fail', 'register_error': 'SPU商品已存在'})


    def put(self, request):
        #不能更改商品分类即category_id,只能修改描述简介和服务
        data = json.loads(request.body)
        spunameb = data.get('spunameb')
        spuname = data.get('spuname')
        spudetail = data.get('spudetail')
        spupack = data.get('spupack')
        spuservice = data.get('spuservice')

        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([spunameb, spuname]):
            return HttpResponseForbidden('缺少必填项')

        # 规格名称是否为1-20个字符；
        # if not re.match(r'^[a-zA-Z0-9_-]{1,20}$', specname):
        #     return HttpResponseForbidden('请输入1-20个字符的规格名称')
        if chinese_len(spuname) > 20:
            return HttpResponseForbidden('请输入1-20个字符的SPU商品名称')

        spubs = SPU.objects.filter(name=spunameb)
        if not spubs:
            return HttpResponseForbidden('当前SPU商品名不存在')
        
        spub = SPU.objects.get(name=spunameb)
        # SPU商品名不重复
        spus = SPU.objects.filter(name=spuname).exclude(id=spub.id)
        if not spus:
            try:
                spub.name=spuname
                spub.desc_detail=spudetail
                spub.desc_pack = spupack
                spub.desc_service = spuservice
                spub.save()
                return JsonResponse({'code': 'ok', 'register_error': f'修改{spunameb} SPU商品 成功'})

            except DatabaseError:
                return JsonResponse({'code': 'fail', 'register_error': '修改SPU商品 失败'})
        else:
            return JsonResponse({'code': 'fail', 'register_error': '此SPU商品名称已存在'})
