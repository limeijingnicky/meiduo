from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseForbidden,HttpResponseNotFound,JsonResponse
from contents.views import get_categories
from django.core.paginator import Paginator,EmptyPage
from goods.models import GoodsCategory,SKU,SKUSpecification,SPUSpecification,SpecificationOption


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

        #查询sku
        context={
            'category': category,
            'breadcrumb': breadc,
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
