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
            # #获取缓存数据
            category1_models_list=cache.get('category1dddd_model_list')

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
                    # cache.set('category1_model_list',category1_models_list,360)
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

                    #缓存
                    cache.set('sub_category_'+category_id,sub_data,360)

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


class CategoryView(View):
    # 权限认证
    permission_classes = [IsAdminUser]
    # 渲染器指定
    renderer_classes = [JSONRenderer]

    def get(self,request,page_num,keyword):
        keyword=request.GET.get('keyword')
        page_num=page_num
        print(f"'keyword':{keyword}")

        categories=[]
         # 当不存在查询参数时，即返回所有规格信息
        if not keyword:
            #查询数据库中的一级分类对象
            cates = GoodsCategory.objects.filter(parent__isnull=True)
            #依次往下查询
            for first_cate in cates:
                categories.append({
                    'id': first_cate.id,
                    'third_category_name': "",
                    'second_category_name': "",
                    'first_category_name': first_cate.name
                })
                second_cates=GoodsCategory.objects.filter(parent_id=first_cate.id)
                for second_cate in second_cates:
                    categories.append({
                        'id': second_cate.id,
                        'third_category_name':"",
                        'second_category_name': second_cate.name,
                        'first_category_name': first_cate.name
                    })
                    third_cates=GoodsCategory.objects.filter(parent_id=second_cate.id)
                    for third_cate in third_cates:
                        categories.append({
                            'id':third_cate.id,
                            'third_category_name':third_cate.name,
                            'second_category_name': second_cate.name,
                            'first_category_name': first_cate.name
                        })

        else:
            categories_id=[]
            #查询数据集
            cates = GoodsCategory.objects.filter(name__contains=keyword)

            if not cates:
                return render(request,'category_admins.html', {'page_categories': categories})
            else:
                for cate in cates:
                    #注意需要去重，因为一级或二级或三级可能同时存在相同字段，检查id
                    if cate.parent_id is None:
                        # 往上找
                        if cate.id not in categories_id:
                            categories_id.append(cate.id)
                            categories.append(
                                {
                                    'id': cate.id,
                                    'third_category_name': "",
                                    'second_category_name': "",
                                    'first_category_name': cate.name
                                }
                            )
                            #往下找
                            #该对象为一级标签
                            second_cates=GoodsCategory.objects.filter(parent_id=cate.id)
                            for second_cate in second_cates:
                                if second_cate.id not in categories_id:
                                    categories_id.append(second_cate.id)
                                    categories.append(
                                        {
                                            'id': second_cate .id,
                                            'third_category_name': '',
                                            'second_category_name': second_cate.name,
                                            'first_category_name': cate.name
                                        }
                                    )

                                    third_cates=GoodsCategory.objects.filter(parent_id=second_cate.id)
                                    for third_cate in third_cates:
                                        if third_cate.id not in categories_id:
                                            categories_id.append(third_cate.id)
                                            categories.append(
                                                {
                                                    'id': third_cate.id,
                                                    'third_category_name': third_cate.name,
                                                    'second_category_name': second_cate.name,
                                                    'first_category_name': cate.name
                                                }
                                            )

                    else:
                        #可能是二级标签，也可能是三级标签,要先判断
                        parent_cate = GoodsCategory.objects.get(id=cate.parent_id)
                        if parent_cate.parent_id is None:
                            #二级标签,稍微复杂一点，既要往下找，又要网上找

                            #往上找
                            if cate.id not in categories_id:
                                categories_id.append(cate.id)
                                categories.append(
                                    {
                                        'id':cate.id,
                                        'third_category_name':"",
                                        'second_category_name':cate.name,
                                        'first_category_name':parent_cate.name
                                    }
                                )

                                #往下找
                                third_cates=GoodsCategory.objects.filter(parent_id=cate.id)
                                for third_cate in third_cates:
                                    if third_cate.id not in categories_id:
                                        categories_id.append(third_cate.id)
                                        categories.append(
                                            {
                                                'id': third_cate.id,
                                                'third_category_name':third_cate.name,
                                                'second_category_name': cate.name,
                                                'first_category_name': parent_cate.name,
                                            }
                                        )
                        else:
                            #三级标签
                            first_cate = GoodsCategory.objects.get(id=parent_cate.parent_id)
                            if cate.id not in categories_id:
                                categories_id.append(cate.id)
                                categories.append(
                                    {
                                        'id': cate.id,
                                        'third_category_name': cate.name,
                                        'second_category_name': parent_cate.name,
                                        'first_category_name': first_cate.name
                                    }
                                )


        paginator = Paginator(categories, 10)
        total_page = paginator.num_pages

        try:
            categoriess = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('当前页面不存在')

        context = {
            'page_categories': categoriess,
            'total_page': total_page,
            'page_num': page_num,
        }
        # print(context)
        # 查询一个作者的所有书籍
        # author_instance = Author.objects.get(id=1)
        # books = author_instance.books.all()（books为Book模型中的关联字段，否则默认为book_set）
        return render(request,'category_admins.html',context=context)

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
        catename = json_dict.get('catename')
        cl1 = json_dict.get('cl1')
        cl2 = json_dict.get('cl2')

        print(f'catename:{catename}')
        print(f'cl1:{cl1}')
        print(f'cl2:{cl2}')

        if chinese_len(catename)>20:
            return HttpResponseForbidden('请输入1-20个字符的类别名称')
        #判断cl1, cl2, cl3是否都存在，从而确认新增哪个级别的，并且确认这个新增级别的parent_id

        #可能是二级或一级类别
        if not cl2:
            if not cl1:
                #一级类别
                if not GoodsCategory.objects.filter(name=catename, parent_id=None):
                    GoodsCategory.objects.create(name=catename, parent_id=None)
                    return JsonResponse({'code': 'ok', 'register_error': f'添加{catename} 一级类别 成功'})
                else:
                    return HttpResponseForbidden('该一级类别已存在')
            else:
                #二级类别
                if not GoodsCategory.objects.filter(name=catename, parent_id=cl1):
                    GoodsCategory.objects.create(name=catename, parent_id=cl1)
                    return JsonResponse({'code': 'ok', 'register_error': f'添加{catename} 二级类别 成功'})
                else:
                    return HttpResponseForbidden('该二级类别已存在')
        else:
            #三级类别
            if not cl1:
                return HttpResponseForbidden('缺少必填类别')
            else:
                if not GoodsCategory.objects.filter(name=catename, parent_id=cl2):
                    GoodsCategory.objects.create(name=catename,parent_id=cl2)
                    return JsonResponse({'code': 'ok', 'register_error': f'添加{catename} 三级类别 成功'})
                else:
                    return HttpResponseForbidden('该三级类别已存在')


