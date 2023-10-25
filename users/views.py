from django.shortcuts import render,redirect
from django.views import View
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
import re
from users.models import Users
from django.db import DatabaseError
from django.urls import reverse
from django.contrib.auth import login,authenticate,logout
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
from QQLoginTool import QQtool
import json
import logging
from celery_tasks.email.tasks import send_verify_email
from itsdangerous import URLSafeSerializer
from itsdangerous import BadSignature
from django.conf import settings
from users.models import Address,Users

##设计子接口逻辑，
# 包括请求方法，get post put delete
# 请求地址，url
# 请求参数，路径参数，查询字符串，表单，json
# 响应数据，响应数据 html json


from django.contrib.auth.mixins import LoginRequiredMixin
class LoginRequiredJSONMixin(LoginRequiredMixin):
  # 重写handle_no_permission方法，直接传出一个jsonresponse
    def handle_no_permission(self):
        # 响应json数据
        return JsonResponse({'code':'406','errmsg':'用户未登录'})


class AddressCreateView(LoginRequiredJSONMixin,View):
    #新增收货地址
    def post(self,request):
        # 判断用户地址数量是否超过可登录上限
        # count= Address.objects.filter(user=request.user).count()
        # 通过外键查询
        count = request.user.addresses.count()
        if count >= 5:
            return JsonResponse({'code': '408', 'errmsg': '已超过最多的地址保存数量'})

        #接收参数
        json_str=request.body.decode()
        json_dict=json.loads(json_str)
        receiver=json_dict.get('receiver')
        province_id=json_dict.get('province_id')
        city_id=json_dict.get('city_id')
        district_id=json_dict.get('district_id')
        place=json_dict.get('place')
        mobile=json_dict.get('mobile')
        email = json_dict.get('email')
        tel= json_dict.get('tel')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[0-9]{10}$', mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^[0-9]{6,10}$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return HttpResponseForbidden('参数email有误')

        #保存地址信息,将地址信息存储在address表格里
        try:
            # address=Address(
            #     user = request.user,
            #     title =receiver,
            #     receiver =receiver,
            #     #外键都是绑定的id
            #     province_id = province_id,
            #     city_id = city_id,
            #     district_id = district_id,
            #     place =place,
            #     mobile =mobile,
            #     tel = tel,
            #     email = email,
            #     # is_deleted = 有默认值
            # )

            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                # 外键都是绑定的id
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
                # is_deleted = 有默认值
            )

            #如果用户没有默认的地址，则需要指定默认的地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            return JsonResponse({'code':'407','errmsg':'数据传输错误'})


        #新增地址成功后，实现网页局部刷新
        # 构造响应数据
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': '0', 'errmsg': '更新地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin,View):
    #查询地址信息
    def get(self,request):
        #当前用户
        user=request.user
        #查找当前对象对应的address类
        addresses=Address.objects.filter(user=user,is_deleted=False)
        # addresses=user.addresses.filter(is_deleted=False)

        #将对象列表化
        address_list=[]
        for address in addresses:
            address_dict={
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)

        context={
            'default_address_id': user.default_address_id,
            'address': address_list
        }
        return render(request,'user_center_site.html',context)



#设置一个激活链接
def generate_varify_email_url(user):
    # 生成秘钥
    secret_key = 'varify_email_url_key'  # 越复杂越安全
    serializer = URLSafeSerializer(secret_key)

    # 生成签名令牌
    data = {'username': user.username, 'email': user.email}
    token = serializer.dumps(data)

    return settings.EMAIL_VERIFY_URL + '?token='+token


def check_varify_email_url(token):
    secret_key = 'varify_email_url_key'  # 越复杂越安全
    serializer = URLSafeSerializer(secret_key)

    try:
        data = serializer.loads(token)
    except BadSignature:
        return None
    else:
        username=data['username']
        email=data['email']
        try:
            user=Users.objects.get(username=username,email=email)
        except Users.DoseNotExist:
            return None
        else:
            return user



class VerifyEmailView(View):
    def get(self,request):
        token = request.GET.get('token')

        if not token:
            return HttpResponseForbidden('没有token')

        user = check_varify_email_url(token)
        if not user:
            return HttpResponseForbidden('token无效')

        try:
            user.email_active=True
            user.save()
        except Exception as e:
            # logger.error(e)
            return HttpResponseForbidden('邮箱激活失败')
        else:
            return redirect('/info/')



class EmailView(LoginRequiredJSONMixin,View):
    #添加邮箱
    def put(self,request):
        json_str=request.body.decode()
        json_dic=json.loads(json_str)
        email=json_dic.get('email')

        # 校验邮箱地址
        if not re.match(r'^\w+@\w+\.\w+$',email):
            return HttpResponseForbidden('email格式不正确')
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            return JsonResponse({'code':405,'errmsg':'添加邮箱失败'})

        # #发送邮箱验证邮件
        verify_url=generate_varify_email_url(request.user)
        message='这是纯文本邮件内容'
        send_verify_email.delay(email,verify_url,message)

        #
        # subject = "美多商城邮箱验证"
        # html_message = '<p>尊敬的用户您好！<p>' \
        #                '<p>感谢您使用美多商城。 <p> ' \
        #                '<p>您的邮箱为：%s。请点击此链接激活您的邮箱：<p> ' \
        #                '<p> <a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        #
        # send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[email],
        #           html_message=html_message)



        return JsonResponse({'code':0,'errmsg':'ok'})


class UserinfoView(LoginRequiredMixin,View):
    #用户中心
    def get(self,request):
        # if request.user.is_authenticated:
        #     return render(request,'user_center_info.html')
        # else:
        #     return redirect('/login')
        # login_url='/login'
        context={
            'username':  request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request,'user_center_info.html',context)



class UserCartView(LoginRequiredMixin,View):
    ##购物车
    def get(self,request):
        return render(request,'cart.html')



class UserOrderView(LoginRequiredMixin, View):
    ##用户订单
    def get(self, request):
        return render(request, 'user_center_order.html')

class LogoutView(View):
    #用户退出登录
    def get(self,request):
        logout(request)
        response = redirect('/')
        response.delete_cookie('username')
        return response


class LoginView(View):
    # 用户登录
    def get(self,request):
        return render(request,'login.html')

    def post(self, request):
        #接收参数
        username=request.POST.get('username')
        password=request.POST.get('password')
        remembered = request.POST.get('remembered')

        #校验参数
        if not all([username,password]):
            return HttpResponseForbidden("缺少必传参数")

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return HttpResponseForbidden("用户名不正确")

        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseForbidden("密码不正确")


        #认证用户
        #在数据库中查询用户名是否存在
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'password_errmsg': '用户名或者密码错误'})


        #状态保持
        login(request,user)
        #使用remembered 状态保持周期
        if remembered !='on':
            #不进行状态保持
            request.session.set_expiry(0)

        else:
            #记住登录：状态保持为1小时
            request.session.set_expiry(60*60)

        #先取出next
        next=request.GET.get('next')
        #如果next存在则重定向到之前页面
        if next:
            response=redirect(next)
        #如果next不存在，则重定向到首页
        else:
            response=redirect('/')

        #为了在首页显示用户名等登录信息，需要将用户名缓存到cookie中
        response.set_cookie('username',user.username,max_age=60*60)


        #响应结果(重定向到之前页面)
        return response



class UsernameCountView(View):
    def get(self,request,username):

        counts = Users.objects.filter(username=username).count()
        if counts == 0:
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': counts})

        else:
            return JsonResponse({'code': 404, 'errmsg': 'error with repeat of id', 'count': counts})

class MobileCountView(View):
    def get(self,request,mobile):
        counts = Users.objects.filter(mobile=mobile).count()
        if counts == 0:
            return JsonResponse({'code': 0, 'errmsg': 'ok', 'count': counts})

        else:
            return JsonResponse({'code': 404, 'errmsg': 'error with repeat of mobile', 'count': counts})






class RegisterView(View):
    #用户注册
    def get(self,request):
        # return HttpResponse('it is ok')
        return render(request,'register.html')


    def post(self,request):
        ##接收参数,表单数据用POST接收，非表单JSON用body收，然后非序列化

        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        # uuid=request.POST.get('uuid')
        sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')



        ##校验参数,前后端逻辑相同
        ##判断参数是否齐全；all(【列表】)方法 ,判断数值是否为空，有一个为空，则返回false
        if not all([username, password,password2,mobile,allow]):
            return HttpResponseForbidden('缺少必填项')

        # 用户名是否为5-20个字符；
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')

        # 密码是否为8-20个字符；
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20个字符的密码')

        # 判断两次输入密码是否一致；
        if password != password2:
            return HttpResponseForbidden('两次输入的密码不一致')

        # 手机号码是否合法；
        if not re.match(r'^1\d{10}$',mobile):
            return HttpResponseForbidden('请输入正确的手机号码')

        # #添加一个校验短信验证码的逻辑
        # redis_con = get_redis_connection('verify_code')
        # sms_code_server = redis_con.get(mobile).decode()
        # if sms_code_server is None:
        #     return render(request,'register.html',{'error_sms_code_tip':'短信验证码已失效'})
        # if sms_code_server != sms_code :
        #     return render(request, 'register.html', {'error_sms_code_tip':'短信验证码输入有误'})



        # 是否勾选了协议
        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议')


        ##保存注册数据 (核心代码)
        ##利用models里的用户表单模型进行数据存储,数据库储存错误就重定向到注册页面


        try: #返回一个对象
            user=Users.objects.create_user(username=username,password=password,mobile=mobile)

        except DatabaseError :
            return render(request,'register.html',{'register_error': '注册失败'})


        ##用户登录状态保持,将用户的信息保存在session里
        login(request,user)

        response = redirect('/')

        # 为了在首页显示用户名等登录信息，需要将用户名缓存到cookie中
        response.set_cookie('username', user.username, max_age=60 * 60)

        ##响应结果:重定向到首页
        # return render(request,template_name='index')

        # return redirect(reverse('content : index')) ##反向解析后得到路由
        return response




