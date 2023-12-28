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
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.cache import cache
from goods.models import GoodsCategory
from views.spu import chinese_len

class CategoryGetView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    #使用get方法，传area_id,代表地区数据id
    def get(self,request):
        category_id = request.GET.get('category_id')

        if not category_id:
            #获取缓存数据
            category1_models_list=cache.get('category1_model_list')

            if not category1_models_list:
                #需要查询省份
                try:
                    category1_models=GoodsCategory.objects.filter(parent__isnull=True)
                    # return render(request,'user_center_site.html') ##可以直接渲染到网页上
                    #需要模型列表转为字典
                    category1_models_list=[]
                    for category1_model in category1_models:
                        p = {
                            'id':  category1_model.id,
                            'name': category1_model.name
                        }
                        category1_models_list.append(p)
                    #将自动加载的省份数据，进行缓存
                    cache.set('category1_model_list',category1_models_list,3600)
                    return JsonResponse({'code': 0, 'errmsg': 'ok', 'category1_list': category1_models_list})

                except Exception as e:
                    return JsonResponse({'code': 418,'errmsg':'查询一级分类错误'})

            return JsonResponse({'code': 0, 'errmsg': 'ok', 'category1_list': category1_models_list})  # 将所有一级名称数据传入页面
        ##先通过一级分类的id，查找下级二级分类和三级分类
        # 多查一时：子集.外键（可以查到主键）
        # 一查多时：主键.关联子集（可以查到关联子集）
        if category_id:

            # 获取缓存数据
            sub_data= cache.get('sub_category_'+category_id)

            if not sub_data:
                try:
                    #先通过省的area_id，确定对象
                    parent_model = GoodsCategory.objects.get(id=category_id)
                    #通过模型的related关系 获得下级对象
                    sub_model = parent_model.subs.all()

                    subs=[]
                    for sub in sub_model:
                        sub_dict={
                            'id':sub.id,
                            'name': sub.name
                        }
                        subs.append(sub_dict)

                    sub_data={
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs
                    }

                    #缓存城市或区县
                    cache.set('sub_category_'+category_id,sub_data,3600)

                except Exception as e:
                    return JsonResponse({
                        'code': 419,
                        'errmsg': '查询二级或三级分类错误',
                    })

            else:
                return JsonResponse({
                    'code':0,
                    'errmsg':'ok',
                    'sub_data': sub_data
                })


# class CategoryView(View):
#     # 权限认证
#     permission_classes = [IsAdminUser]
#     # 渲染器指定
#     renderer_classes = [JSONRenderer]
#
#     def get(self,request,page_num,keyword):
#         keyword=request.GET.get('keyword')
#         page_num=page_num
#
#
#         categories=[]
#          # 当不存在查询参数时，即返回所有规格信息
#         if not keyword:
#             #查询数据库中的一级分类对象
#             cates = GoodsCategory.objects.filter(parent__isnull=True)
#             #依次往下查询
#             for cate in cates:
#
#
#         else:
#             cates = GoodsCategory.objects.filter(name__contains=keyword)
#             if not cates:
#                 return render(request,'category_admins.html', {'page_categories': categories})
#
#
#         spuu=[]
#         for spu in spus:
#             spuu.append(
#                 {
#                     'spuid' : spu.id,
#                     'spuname' : spu.name,
#                     'spudetail' : spu.desc_detail,
#                     'spupack': spu.desc_pack,
#                     'spuservice': spu.desc_service
#                 }
#             )
#         print(spuu)
#
#         paginator = Paginator(spuu, 2)
#         total_page = paginator.num_pages
#
#         try:
#             spuss = paginator.page(page_num)
#         except EmptyPage:
#             return HttpResponseNotFound('当前页面不存在')
#
#         context = {
#             'page_spus': spuss,
#             'total_page': total_page,
#             'page_num': page_num,
#         }
#         # print(context)
#         # 查询一个作者的所有书籍
#         # author_instance = Author.objects.get(id=1)
#         # books = author_instance.books.all()（books为Book模型中的关联字段，否则默认为book_set）
#         return render(request,'spus_admins.html',context=context)

class CategoryAddView(View):
    """
    添加商品分类
    """
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def post(self,request):
        """
        添加商品分类
        :param request:
        :return:
        """
        json_dict = json.loads(request.body.decode())
        parent_category_name = json_dict.get('name')
        second_category_name = json_dict.get('name')
        third_category_name  = json_dict.get('name')


        #判断是否为空
        if not all([parent_category_name,second_category_name,third_category_name]):
            return HttpResponseForbidden(request,'参数不全')

        if chinese_len(parent_category_name)>20:
            return HttpResponseForbidden('请输入1-20个字符的类别名称')
        if chinese_len(second_category_name) > 20:
            return HttpResponseForbidden('请输入1-20个字符的类别名称')
        if chinese_len(third_category_name) > 20:
            return HttpResponseForbidden('请输入1-20个字符的类别名称')


        #先判断一级类别是否存在
        parent = GoodsCategory.objects.filter(name=parent_category_name,parent_id=None)
        if not parent:
            try:
                new_p_category=GoodsCategory.objects.create(name=parent_category_name,parent_id=None)
                new_s_category = GoodsCategory.objects.create(name=second_category_name, parent_id=new_p_category.id)
                new_t_category = GoodsCategory.objects.create(name=third_category_name, parent_id=new_s_category.id)
                return JsonResponse({'code': 'ok', 'register_error': f'添加{parent_category_name} 新类别 成功'})
            except Exception as e:
                return JsonResponse({'code': 'fail', 'register_error': '添加新类别 失败'})
        else:
            p_category_id = GoodsCategory.objects.get(name=parent_category_name, parent_id=None).id
            s_category = GoodsCategory.objects.filter(name=second_category_name, parent_id=p_category_id)
            if not s_category:
                try:
                    new_s_category = GoodsCategory.objects.create(name=second_category_name,parent_id=p_category_id)
                    new_t_category = GoodsCategory.objects.create(name=third_category_name, parent_id=new_s_category.id)
                    return JsonResponse({'code': 'ok', 'register_error': f'添加{second_category_name} 新类别 成功'})
                except Exception as e:
                    return JsonResponse({'code': 'fail', 'register_error': '添加新类别 失败'})
            else:
                s_category = GoodsCategory.objects.get(name=second_category_name, parent_id=p_category_id)
                t_category = GoodsCategory.objects.filter(name=second_category_name, parent_id=s_category.id)
                if not t_category:
                    try:
                        GoodsCategory.objects.create(name=third_category_name, parent_id=s_category.id)
                        return JsonResponse({'code': 'ok', 'register_error': f'添加{third_category_name} 新类别 成功'})
                    except Exception as e:
                        return JsonResponse({'code': 'fail', 'register_error': '添加新类别 失败'})
                else:
                    return JsonResponse({'code': 'fail', 'register_error': '类别已存在'})
