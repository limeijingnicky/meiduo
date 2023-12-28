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


class SpecsView(View):
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
                return render(request,'specs_admins.html', {'page_specs': spuid})

        #根据模型之间的外键进行关联查询
        specs=[]
        for spuu in spus:
            sname=spuu.name
            spui=spuu.id
            #通过外键查询方法，查询所有对象
            s=spuu.specs.all()

            #遍历每个对象，储存数据
            for ss in s:
                specs.append(
                    {
                        'id':ss.id,
                        'spuid':spui,
                        'spuname':ss.name,
                        'sname':sname
                    }
                )
        # print(specs)

        paginator = Paginator(specs, 2)
        total_page = paginator.num_pages

        try:
            specss = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('当前页面不存在')

        context = {
            'page_specs': specss,
            'total_page': total_page,
            'page_num': page_num,
        }
        # print(context)
        # 查询一个作者的所有书籍
        # author_instance = Author.objects.get(id=1)
        # books = author_instance.books.all()（books为Book模型中的关联字段，否则默认为book_set）
        return render(request,'specs_admins.html',context=context)


def chinese_len(text):
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')  # Match Chinese characters

    # Count the number of Chinese characters in the text
    chinese_characters = re.findall(chinese_pattern, text)
    chinese_length = len(chinese_characters)

    return chinese_length


class SpecsAddView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def post(self,request):

        data = json.loads(request.body)
        specname = data.get('specname')
        spuname = data.get('spuname')
        # print(specname)
        # print(spuname)
        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([specname, spuname]):
            return HttpResponseForbidden('缺少必填项')

        # 规格名称是否为1-20个字符；
        # if not re.match(r'^[a-zA-Z0-9_-]{1,20}$', specname):
        #     return HttpResponseForbidden('请输入1-20个字符的规格名称')
        if chinese_len(specname)>20:
            return HttpResponseForbidden('请输入1-20个字符的规格名称')

        # SPU商品名称是否为1-20个字符；
        # if not re.match(r'^[0-9a-zA-Z]{1,20}$', spuname):
        #     return HttpResponseForbidden('请输入1-20个字符的SPU商品名称')
        if chinese_len(spuname)> 20:
            return HttpResponseForbidden('请输入1-20个字符的SPU商品名称')

        #SPU商品名要存在
        spus = SPU.objects.filter(name=spuname)
        if spus:
            for spu in spus:
                #规格名称不能重复
                spu_id=spu.id
                if not SPUSpecification.objects.filter(name=specname,spu_id=spu_id):
                    try:  # 返回一个对象
                        spe = SPUSpecification.objects.create(name=specname,spu_id=spu_id)
                        return JsonResponse({'code': 'ok','register_error':f'添加{specname} 规格 成功'})

                    except DatabaseError:
                        return JsonResponse({'code': 'fail','register_error': '添加规格失败'})
                else:
                    return JsonResponse({'code': 'fail', 'register_error': '规格已存在'})
        else:
            return JsonResponse({'code': 'fail', 'register_error': 'SPU商品不存在'})

    def put(self, request):

        data = json.loads(request.body)
        specnameb = data.get('specnameb')
        specname = data.get('specname')
        spuname = data.get('spuname')
        print(specname)
        print(spuname)
        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([specname, spuname]):
            return HttpResponseForbidden('缺少必填项')

        # 规格名称是否为1-20个字符；
        # if not re.match(r'^[a-zA-Z0-9_-]{1,20}$', specname):
        #     return HttpResponseForbidden('请输入1-20个字符的规格名称')
        if chinese_len(specname) > 20:
            return HttpResponseForbidden('请输入1-20个字符的规格名称')

        # SPU商品名称是否为1-20个字符；
        # if not re.match(r'^[0-9a-zA-Z]{1,20}$', spuname):
        #     return HttpResponseForbidden('请输入1-20个字符的SPU商品名称')
        if chinese_len(spuname) > 20:
            return HttpResponseForbidden('请输入1-20个字符的SPU商品名称')

        # SPU商品名要存在
        spus = SPU.objects.filter(name=spuname)
        if spus:
            for spu in spus:
                # 规格名称不能重复
                spu_id = spu.id
                if SPUSpecification.objects.filter(name=specnameb,spu_id=spu_id):
                    try:  # 返回一个对象 update用来批量更新数据，不返回对象。
                          #如果想返回对象，则配合使用get（），然后修改对应字段：instance.name=new_name 然后save（）
                        spe = SPUSpecification.objects.filter(name=specnameb,spu_id=spu_id).update(name=specname)
                        return JsonResponse({'code': 'ok', 'register_error': f'修改{specname} 规格 成功'})

                    except DatabaseError:
                        return JsonResponse({'code': 'fail', 'register_error': '修改规格失败'})
                else:
                    return JsonResponse({'code': 'fail', 'register_error': '当前规格不存在'})
        else:
            return JsonResponse({'code': 'fail', 'register_error': 'SPU商品不存在'})


class SpecsDeleteView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def post(self, request):
        data = json.loads(request.body)
        specname = data.get('specname')
        spuname = data.get('spuname')
        print(specname)
        print(spuname)


        # SPU商品名要存在
        spus = SPU.objects.filter(name=spuname)
        if spus:
            for spu in spus:
                # 规格名称
                spu_id = spu.id
                if SPUSpecification.objects.filter(name=specname,spu_id=spu_id):
                    try:  # 返回一个对象 update用来批量更新数据，不返回对象。
                          #如果想返回对象，则配合使用get（），然后修改对应字段：instance.name=new_name 然后save（）
                        spe = SPUSpecification.objects.get(name=specname,spu_id=spu_id).delete()
                        return JsonResponse({'code': 'ok', 'register_error': f'删除{specname} 规格 成功'})

                    except DatabaseError:
                        return JsonResponse({'code': 'fail', 'register_error': '删除规格失败'})
                else:
                    return JsonResponse({'code': 'fail', 'register_error': '当前规格不存在'})
        else:
            return JsonResponse({'code': 'fail', 'register_error': 'SPU商品不存在'})

