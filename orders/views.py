from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from users.models import Address
from goods.models import SKU
from django.http import JsonResponse
from django_redis import get_redis_connection

class OrderSettlemnetView(LoginRequiredMixin,View):

    def get(self,request):
        #查询展示订单数据
        #查询用户
        user=request.user

        #查询收货地址
        try:
            addresses=user.addresses.filter(is_deleted=False)
        except Address.DoesNotExist:
            addresses=None

        #查询购物车中被勾选的商品信息
        redis_conn=get_redis_connection('carts')
        item_dict=redis_conn.hgetall('carts_%s'%user.id)
        cart_selected=redis_conn.smembers('cart_selected_%s'%user.id)
        #因为取出的值为十六进制所以要int（）强制转换
        selected_item= {}
        for sku_id in cart_selected:
            selected_item[int(sku_id)]=int(item_dict[sku_id])

        sku_ids=selected_item.keys()
        skus=SKU.objects.filter(id__in=sku_ids)

        total_c=0
        total_a=0
        for sku in skus:
            #增加一个count和金额的属性
            sku.count=selected_item[sku.id]
            total_c=total_c+sku.count
            sku.amount=sku.count * sku.price
            total_a=total_a+sku.amount

        freight=10.00
        context={
            'address':addresses,
            'skus':skus,
            'total_count':total_c,
            'total_amount':total_a,
            'freight':freight,
            'total_payment':freight+total_a
        }

        return render(request,'place_order.html',context)


