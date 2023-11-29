from django.shortcuts import render
from users.views import LoginRequiredMixin
from django.views import View
from users.models import Address
from goods.models import SKU
from django.http import JsonResponse
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django.http import HttpResponseForbidden,JsonResponse
from orders.models import OrderInfo,OrderGoods
from django.utils import timezone
from django.db import transaction

class OrderSuccessView(LoginRequiredMixin,View):
    def get(self,request):
        '''提交订单成功页面'''
        order_id=request.GET.get('order_id')
        payment_amount=request.GET.get('payment_amount')
        pay_method=request.GET.get('pay_method')
        context={
            'order_id':order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request,'order_success.html',context)

class OrderCommitView(LoginRequiredMixin,View):
    def post(self,request):
        '''提交订单数据'''
        json_dict=json.loads(request.body.decode())
        user=request.user
        address_id=json_dict.get('address_id')




class OrderCommitView(LoginRequiredMixin,View):

    def post(self,request):
        # 1.接收参数,address_id,支付方式
        json_dict=json.loads(request.body.decode())
        address_id=json_dict.get('address_id')
        pay_method=json_dict.get('pay_method')
        # 2.校验参数
        if not all([address_id,pay_method]):
            return HttpResponseForbidden('缺少必传参数')
        try:
            address=Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return HttpResponseForbidden('无效地址')
        #判断支付方式
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return HttpResponseForbidden('无效支付方式')
        #保存订单信息,向mysql插入新数据(一)
        user=request.user
        #阻止mysql先提交事务，因为后面如果库存不够，那么前面也不能提交数据，绑定一起
        with transaction.atomic():

            #在数据库操作之前需要指定保存点，可以随时复原（回滚）数据
            save_id=transaction.savepoint()
            try:
                order=OrderInfo.objects.create(
                    order_id=timezone.localtime().strftime('%Y%m%d%H%M%S')+('%09d'%user.id),#时间+用户id(使用%09d方式强制占9位数)
                    total_count=0,
                    order_amount=Decimal(0.00),
                    freight=Decimal(10.00),
                    pay_method=pay_method,
                    # status= 'UNPAID'if pay_method=='ALIPAY' else 'UNSEND',
                    status=OrderInfo.ORDER_STATE_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
                    OrderInfo.ORDER_STATE_ENUM['UNSEND'],
                    address=address,
                    user=user
                )
                #保存订单商品信息(多)
                redis_conn=get_redis_connection('carts')
                cart_dict=redis_conn.hgetall('carts_%s' %user.id)
                selected=redis_conn.smembers('selected_%s' %user.id)
                new_cart_dict={}
                for cart in cart_dict.keys():
                    if cart in selected:
                        new_cart_dict[int(cart)]=int(cart_dict[cart])

                for sku_id,count in new_cart_dict.items():
                    #当前商品
                    while True:
                        sku=SKU.objects.get(id=sku_id)

                        origin_stock=sku.stock
                        origin_sales=sku.sales

                        if count <= origin_stock:

                            ##设置乐观锁，判断当前库存（查询）是否等于原始库存（没人抢），下单成功，改变数据
                            new_stock = origin_stock - count
                            new_sales = origin_sales + count
                            result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                            # 如果更新时，原始数据变化了，资源抢夺,返回值为0,继续买当前商品，直到真实库存不足为止
                            if result==0:
                                continue #继续下单当前sku,代码往上走

                            #result==1,成功下单
                            sku.spu.sales += count
                            sku.spu.save()

                            OrderGoods.objects.create(
                                order = order,
                                sku = sku,#调用redis数据里的信息
                                count = count,#要与库存比较
                                price = SKU.objects.get(id=sku_id).price
                            )
                            # #减库存，加销量
                            # sku.stock -= count
                            # sku.sales += count
                            # sku.save()
                            #
                            # sku.spu.sales += count
                            # sku.spu.save()
                            # 累加总订单数量和总价
                            order.total_count += count
                            order.order_amount += count * sku.price
                            break
                        else:
                            #库存不足,进行回滚
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code':'505','errmsg':'库存不足'})

                # 一个订单只产生一次运费
                order.order_amount += order.freight
                order.save()

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                JsonResponse({'code': '506', 'errmsg': '订单保存失败'})
            #数据库操作成功，递交一次事务
            transaction.savepoint_commit(save_id)

        return JsonResponse({'code':'0','errmsg':'已下单','order_id': order.order_id})

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
        item_dict=redis_conn.hgetall('carts_%s' %user.id)
        cart_selected=redis_conn.smembers('selected_%s' %user.id)
        #因为取出的值为十六进制所以要int（）强制转换
        selected_item= {}
        for sku_id in cart_selected:
            selected_item[int(sku_id)]=int(item_dict[sku_id])

        sku_ids=selected_item.keys()
        skus=SKU.objects.filter(id__in=sku_ids)

        total_c=0
        total_a=Decimal(0.00) #统一双精
        for sku in skus:
            #增加一个count和金额的属性
            sku.count=selected_item[sku.id]
            total_c=total_c+sku.count
            sku.amount=sku.count * sku.price #price为双精度类型
            total_a=total_a+sku.amount

        freight=Decimal(10.00)
        context={
            'addresses': addresses,
            'skus': skus,
            'total_count': total_c,
            'total_amount': total_a,
            'freight': freight,
            'total_payment': freight+total_a
        }

        return render(request,'place_order.html',context)


