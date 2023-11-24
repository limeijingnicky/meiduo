import base64
import pickle
from itertools import chain
from django.shortcuts import render
from django.views import View
import json
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from goods import models
from django_redis import get_redis_connection
from goods.models import SKU


class CartsView(View):
    # 添加购物车，登录时存储到redis数据库，未登录时存储到cookie
    def post(self, request):
        # 接收参数,sku_id,count,selected
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验
        if not all([sku_id, count]):
            return HttpResponseForbidden('缺少必传参数')

        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return HttpResponseForbidden('sku_id不存在')

        try:
            count = int(count)
            if count > 5 or count < 0:
                return HttpResponseForbidden('count值异常')
        except Exception as e:
            return HttpResponseForbidden('count错误')

        if selected:
            if not isinstance(selected, bool):  # 校验是否为布尔值
                return HttpResponseForbidden('selected 异常')
        # 判断用户是否登录
        user = request.user
        # 已登录，redis
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 增量计算
            redis_conn.hincrby(f'carts_{user.id}', sku_id, count)
            # 添加被选择的
            if selected:
                redis_conn.sadd(f'selected_{user.id}', sku_id)
            return JsonResponse({'code': '0', 'errmsg': '已保存到购物车'})
        # 未登录，cookie
        else:
            # 获取购物车的数据,或者创建新的cookie

            if request.COOKIES.get('carts'):  # 存在cookie时，解码内容
                cart_str = request.COOKIES.get('carts')
                b = cart_str.encode()
                s = base64.b64decode(b)
                cart_dict = pickle.loads(s)
            else:
                cart_dict = {}
            # 判断要添加的商品在cookie中是否存在
            if sku_id not in cart_dict.keys():  # 不存在时，新建
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            else:  # 存在时，进行同类增量计算
                o_count = cart_dict[sku_id]['count']
                cart_dict[sku_id] = {
                    'count': o_count + count,
                    'selected': selected
                }

            # 将cart_dict写入cookies
            cart_s = pickle.dumps(cart_dict)
            cart_b = base64.b64encode(cart_s)
            cart_st = cart_b.decode()

            response = JsonResponse({'code': '0', 'errmsg': '已添加到购物车'})
            response.set_cookie('carts', cart_st)

            return response

    # 查询购物车
    def get(self, request):
        user = request.user
        cart_dict_redis = {}
        cart_dict_cookies = {}

        if user.is_authenticated:  # 登录用户查询redis
            redis_conn = get_redis_connection('carts')

            # 查询hash列表数据（user_id，sku_id）和set数据（user_id,selected_sku_id）
            redis_sku_id = redis_conn.hgetall(f'carts_{user.id}')
            redis_selected = redis_conn.smembers(f'selected_{user.id}')

            # 重新构建一个字典,与cookie格式相同
            for sku_id, count in redis_sku_id.items():
                cart_dict_redis[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }

        # 查询未登录时的cookies数据
        if request.COOKIES.get('carts'):  # 存在cookie时，解码内容
            cart_str = request.COOKIES.get('carts')
            b = cart_str.encode()
            s = base64.b64decode(b)
            cart_dict_cookies = pickle.loads(s)

        # print("cart_dict_cookies:", cart_dict_cookies)

        # 合并登录数据和未登录数据,并构建出

        keys_redis = cart_dict_redis.keys()
        keys_cookies = cart_dict_cookies.keys()

        # 读取redis里的数据 和cookie里的数据
        skus_redis = SKU.objects.filter(id__in=keys_redis)
        skus_cookies = SKU.objects.filter(id__in=keys_cookies)

        # Check if either queryset is None before merging
        if skus_redis is not None and skus_cookies is not None:
            merged_skus = list(chain(skus_redis, skus_cookies))
        else:
            # Handle the case where either skus_redis or skus_cookies is None
            merged_skus = skus_redis if skus_cookies is None else skus_cookies


        sku_dict = []
        sku_repeat=[]
        for skuu in merged_skus:
            if skuu.id not in sku_repeat:
                sku_repeat.append(skuu.id)

                try:
                    count_redis = cart_dict_redis.get(skuu.id,{}).get('count', 0)
                    selected_redis = cart_dict_redis.get(skuu.id,{}).get('selected', False)
                    count_cookies = cart_dict_cookies.get(skuu.id,{}).get('count', 0)
                    selected_cookies = cart_dict_cookies.get(skuu.id,{}).get('selected', False)

                except Exception as e:
                    count_redis = 0
                    selected_redis = False

                    count_cookies = 0
                    selected_cookies = False

                total_count = count_redis + count_cookies
                t_selected = selected_redis or selected_cookies

                sku_dict.append(
                    {
                        'id': skuu.id,
                        'count': total_count,
                        'selected': str(t_selected),
                        'name': skuu.name,
                        # 'default_image_url': sku.default_image_url,
                        'price': str(skuu.price),
                        'amount': str(skuu.price * total_count)
                })

        context={
            'cart_skus': sku_dict
        }

        response = render(request, 'cart.html', context)

        #将cookies里的数据，同步到redis里，并且同时删除cookie里的数据（因为有可能随时登录）
        if user.is_authenticated and request.COOKIES.get('carts'):
            redis_conn = get_redis_connection('carts')

            for keys, values in cart_dict_cookies.items():
                count = values.get('count',0)
                selected = values.get('selected',False)

                if not redis_conn.hexists(f'carts_{user.id}',keys):  # redis不已存在时，新建
                    redis_conn.hset(f'carts_{user.id}', keys, count)
                    if selected:
                        redis_conn.sadd(f'selected_{user.id}', keys)
                else:  # 存在时，进行同类增量计算
                    o_c=int(redis_conn.hget(f'carts_{user.id}', keys) or 0)
                    n_c=o_c+count
                    redis_conn.hset(f'carts_{user.id}', keys, n_c)
                    if selected:
                        redis_conn.sadd(f'selected_{user.id}', keys)

            # 删除名为 'carts' 的 cookie
            response.delete_cookie('carts')

        return response

    #修改购物车
    def put(self,request):
        #接收和校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id, count]):
            return HttpResponseForbidden('缺少参数')

        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return HttpResponseForbidden('商品sku_id不存在')

        try:
            count = int(count)
            if count < 0:
                return HttpResponseForbidden('商品count值异常')
        except Exception as e:
            return HttpResponseForbidden('商品count错误')

        if selected:
            if not isinstance(selected, bool):  # 校验是否为布尔值
                return HttpResponseForbidden('商品selected 异常')

        # 判断用户是否登录，登录用户覆盖写入sku_id,count,selected
        # 未登录用户，只能修改cookies里的内容
        cart_dict = {}
        if request.COOKIES.get('carts'):  # 存在cookie时，解码内容
            cart_str = request.COOKIES.get('carts')
            b = cart_str.encode()
            s = base64.b64decode(b)
            cart_dict = pickle.loads(s)

        user = request.user
        if user.is_authenticated:
            redis_conn=get_redis_connection('carts')
            redis_conn.hset(f'carts_{user.id}',sku_id,count)
            if selected:
                redis_conn.sadd(f'selected_{user.id}',sku_id)
            else: #去掉勾选
                redis_conn.srem(f'selected_{user.id}',sku_id)

            #将修改后的数据重新传
            cart_sku={
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': SKU.objects.get(id=sku_id).name,
                # 'default_image_url': sku.default_image_url,
                'price': SKU.objects.get(id=sku_id).price,
                'amount': SKU.objects.get(id=sku_id).price * count
            }

            response = JsonResponse({'code': '0', 'errmsg': '已修改购物车','cart_sku': cart_sku})

        else:
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cart_dict写入cookies
            cart_s = pickle.dumps(cart_dict)
            cart_b = base64.b64encode(cart_s)
            cart_str = cart_b.decode()

            #将修改后的数据重新传
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': SKU.objects.get(id=sku_id).name,
                # 'default_image_url': sku.default_image_url,
                'price': SKU.objects.get(id=sku_id).price,
                'amount': SKU.objects.get(id=sku_id).price * count
            }

            response = JsonResponse({'code': '0', 'errmsg': '已修改购物车','cart_sku': cart_sku})
            response.set_cookie('carts', cart_str)

        return response

    #删除购物车
    def delete(self,request):
        # 获取参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden( '商品不存在')

        #判断用户是否登录
        user=request.user
        if user.is_authenticated:
            #登录用户，直接删除redis数据库
            redis_conn=get_redis_connection('carts')
            redis_conn.hdel('carts_%s' % user.id,sku_id)
            redis_conn.srem('selected_%s' % user.id, sku_id)
            return JsonResponse({'code': '0','errmsg':'删除成功'})
        else:
            #未登录用户
            cookie_cart=request.COOKIES.get('carts')
            if cookie_cart:
                cookie_cart_dict=pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cookie_cart_dict={}
            response = JsonResponse({'code': '0', 'errmsg': '删除成功'})
            if sku_id in cookie_cart_dict:
                del cookie_cart_dict[sku_id]
            #将删除后的字典重新写入cookie
            cookie_cart_str=base64.b64encode(pickle.dumps(cookie_cart_dict)).decode()
            response.set_cookie('carts', cookie_cart_str)
        return response



