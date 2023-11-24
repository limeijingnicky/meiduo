import json

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseForbidden,HttpResponseNotFound,JsonResponse
from contents.views import get_categories
from django.core.paginator import Paginator,EmptyPage
from goods.models import GoodsCategory,SKU,SKUSpecification,SPUSpecification,SpecificationOption,GoodsVisitCount
from django.utils import timezone
from datetime import datetime
#封装面包屑导航函数
def breadcrumb(category):
    # 面包屑导航 ,自行判断为几级标签
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': ''
    }

    if not category.parent: #没有父级时为一级标签
        breadcrumb['cat1'] = category

    elif category.subs.count()==0: #没有子级时为三级标签
        breadcrumb['cat1']= category.parent.parent
        breadcrumb['cat2'] = category.parent
        breadcrumb['cat3'] = category

    else: #为二级标签s
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category

    return breadcrumb



class DetailVisitView(View):
    #统计商品访问量
    def post(self,request,category_id):
        #传入参数和校验参数
        try:
            goods=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return HttpResponseForbidden('category_id不存在')

        # # 统计访问量
        # t = timezone.localdate()
        # date_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # date = datetime.strptime(date_str, '%Y-%m-%d')
        #
        # try:
        #     good_visit=goods.goodsvisitcount_set.get(date=date,category_id=category_id)
        #     good_visit.count=good_visit.count+1
        #     good_visit.save()
        # except GoodsVisitCount.DoesNotExist:
        #     GoodsVisitCount.objects.create(date=date, category_id=category_id, count=1)
        # return JsonResponse({'code':0,'errmsg':'已完成统计'})

        # 获取当天的日期
        t=timezone.localdate()
        # 分别读取出年月日
        date_str='%d-%02d-%02d' % (t.year,t.month,t.day)
        date=datetime.strptime(date_str,'%Y-%m-%d')
        try:
            goods_visit=GoodsVisitCount.objects.get(date=date,category=goods)
        except GoodsVisitCount.DoesNotExist:
            goods_visit=GoodsVisitCount() #实例化一个对象
        try:
            goods_visit.category=goods
            goods_visit.date=date
            goods_visit.count=goods_visit.count+1
            goods_visit.save()
        except Exception as e:
            return JsonResponse({'code': 420, 'errmsg': '统计搜索记录失败'})

        return JsonResponse({'code': 0, 'errmsg': '统计搜索记录成功'})

#建立商品详情页面
class DetailView(View):
    def get(self,request,sku_id):
        #接收参数
        try:
            sku=SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request,'404.html')

        #插入商品分类导航
        category = get_categories()

        #插入面包屑导航栏
        breadc = breadcrumb(sku.category)


        # 要求所有规格必须填写
        # # 构建当前规格键
        # # 找到sku对应的SKUSpecification对象
        # sku_specs = sku.specs.order_by('spec_id')
        # sku_key=[]
        # # 循环读取所有规格的选项卡
        # for spec in sku_specs:
        #     sku_key.append(spec.option.id)
        # # 获取当前商品的所有SKU
        # skus = sku.spu.sku_set.all()
        # # 构建不同规格参数（选项）的sku字典
        # spec_sku_map = {}
        # for s in skus:
        #     # 获取sku的规格参数
        #     s_specs = s.specs.order_by('spec_id')
        #     # 用于形成规格参数-sku字典的键
        #     key = []
        #     for spec in s_specs:
        #         key.append(spec.option.id)
        #     # 向规格参数-sku字典添加记录
        #     spec_sku_map[tuple(key)] = s.id
        # # 获取当前商品的规格信息
        # goods_specs = sku.spu.specs.order_by('id')
        # # 若当前sku的规格信息不完整，则不再继续
        # if len(sku_key) < len(goods_specs):
        #     return
        # for index, spec in enumerate(goods_specs):
        #     # 复制当前sku的规格键
        #     key = sku_key[:]
        #     # 该规格的选项
        #     spec_options = spec.options.all()
        #     for option in spec_options:
        #         # 在规格参数sku字典中查找符合当前规格的sku
        #         key[index] = option.id
        #         option.sku_id = spec_sku_map.get(tuple(key))
        #     spec.spec_options = spec_options


        # 获取全部的options
        # 构建当前规格键
        # 找到sku对应的SKUSpecification对象下的所有规格信息
        # spu = sku.spu
        # sku_specs=spu.specs.all()
        #
        # goods_specs = {}
        # # 循环读取当前商品的所有规格信息
        # for sku_spec in sku_specs:
        #     value=[]
        #     # 循环遍历规格选项
        #     for option in sku_spec.options.all():
        #         value.append(option.value)
        #     goods_specs[sku_spec.name] = value

        # 获取当前options

        spu = sku.spu
        sku_specs=spu.specs.filter(spu=spu)

        goods_specs = {}
        for sku_spec in sku_specs:
            value=[]
            options=sku.specs.filter(spec=sku_spec)
            for option in options:
                value.append(option.option)
            goods_specs[sku_spec.name]=value

        #查询sku
        context={
            'category': category,
            'breadcrumb': breadc,
            'sku': sku,
            'specs': goods_specs,
        }
        #响应
        return render(request,'detail.html',context)

class HotView(View):
    #商品热销排行,取销量最高的前两个
    def get(self,request,category_id):
        skus =SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]

        #序列化器
        hot_skus=[]
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                # 'default_image_url': sku.default_image_url,
                'name': sku.name,
                'price': sku.price
            })
        return JsonResponse({'code': 0,'errmsg': 'ok','hot_skus': hot_skus})



class GoodsListView(View):

    def get(self,request,category_id,page_num,sort):
        try:
            category=GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return HttpResponseForbidden('无法查询category_id')

        categories = get_categories()

        #面包屑查询
        breadc = breadcrumb(category)

        #将前端传进来的sort字段，转换为数据库中的字段属性
        sort=request.GET.get('sort','default')
        if sort == 'price':
            sort_field='price'
        elif sort == 'hot':
            sort_field='-sales' #销量倒序排列，从高到低
        else:
            sort='defalut'
            sort_field='create_time'


        #分页和排序查询（sku信息）
        skus=category.sku_set.filter(is_launched=True).order_by(sort_field)
        #将所有产品进行分页
        paginator= Paginator(skus,5)
        #获取当前页的数据和总页数
        try:
            page_skus=paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('当前页面不存在')
        total_page=paginator.num_pages



        context={
            'category_id': category_id,
            'categories': categories,
            'breadcrumb': breadc,
            'page_skus': page_skus,
            'total_page': total_page,
            'page_num': page_num,
            'sort': sort,
        }


        return render(request,'list.html',context=context)



