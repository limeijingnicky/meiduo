from django.shortcuts import render,redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.http import JsonResponse,HttpResponseForbidden,HttpResponseServerError,HttpResponse,HttpResponseRedirect
import logging
from oauth.models import OAuthQQUser
from django.contrib.auth import login
from itsdangerous import URLSafeSerializer
from itsdangerous import BadSignature
import re
from django_redis import get_redis_connection
from users.models import Users

#创建日志输出器
logger=logging.getLogger('django')



class QQAuthUserView(View):
    def get(self,request):

        # openid = request.GET.get('code')
        # if code is None:
        #     return HttpResponseForbidden('获取code失败')

        # appid = settings.QO_CLIENT_ID
        # appkey = settings.QQ_CLIENT_SECRET
        # redirect_uri = settings.Q0_REDIRECT_URI
        #
        # oauth = OAuthQQ(client_id=appid, client_secret=appkey, redirect_uri=redirect_uri)

        # try:
        #     #使用code获取access——token
        #     access_token=oauth.get_access_token(code)
        #
        #     #使用access——token 获取openid
        #     openid=oauth.get_open_id(access_token)

        # except Exception as e:
        #     logger.error(e)
        #     return HttpResponseServerError('oauth2.0认证失败')



        openid = request.GET.get('openid')

        #生成秘钥
        secret_key = 'openid-key' #越复杂越安全
        serializer = URLSafeSerializer(secret_key)
        # 生成签名令牌
        data = {'open_id': openid}
        token = serializer.dumps(data)

        try:
            oauth_user=OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 当不存在时,后面需要关联已存在的用户名或者新建一个用户
            context={'openid': token}
            return render(request,'oauth_callback.html',context)

        else:
            #当存在时，就是已经关联时
            login(request,oauth_user.user)

            response = redirect('/')
            response.set_cookie('username',oauth_user.user.username,max_age=3600*24*15)

            return response


    def post(self, request):
        # 接收参数
        mobile= request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid_client=request.POST.get('openid')

        # 校验参数
        if not all([mobile, password, sms_code_client]):
            return HttpResponseForbidden("缺少必须参数")

        if not re.match(r'^1\d{10}$', mobile):
            return HttpResponseForbidden("手机号不正确")

        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseForbidden("重新输入密码")

        ##判断短信验证码是否一致
        redis_conn=get_redis_connection('verify_code')
        sms_code_server=redis_conn.get(mobile).decode()  ##一定记得解码

        if sms_code_server is None:
            return render(request,'oauth_callback.html', {'sms_code_errmsg': '无效短信验证码'})
        if sms_code_server != sms_code_client:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入正确的短信验证码'})


        #判断openid是否需有效
        secret_key = 'openid-key'  # 越复杂越安全
        serializer = URLSafeSerializer(secret_key)
        try:
            data=serializer.loads(openid_client)
        except BadSignature:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})
        else:
            openid_ = data['open_id']


        # 使用手机号查询对应的用户是否存在
        try:
            user=Users.objects.get(mobile=mobile)
        except Users.DoesNotExist: #新用户,直接注册
            user=Users.objects.create_user(username=mobile,password=password,mobile=mobile)
        else:
            #用户已存在时，检查用户密码是否正确
            if not user.check_password(password):
                # 密码不正确
                return render(request, 'oauth_callback.html', {'qq_login_errmsg': '密码不正确'})

        #密码正确，关联openid和user
        try:
            oauth_qq_user=OAuthQQUser(user=user,openid=openid_)
            oauth_qq_user.save()
        except Exception as e:
            logger.error(e)
            return render(request,'oauth_callback.html', {'qq_login_errmsg': '无法关联账号'})

        #状态保持
        login(request, user)

        #重定向
        # next=request.GET.get('state')
        response = redirect('/')

        # #cookies写入用户名
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        #响应结果
        return response



class QQAuthURLView(View):
    #提供qq登录页面
    def get(self,request):
        #接收next
        next=request.GET.get('next')

        appid=settings.QO_CLIENT_ID
        appkey=settings.QQ_CLIENT_SECRET
        redirect_uri=settings.Q0_REDIRECT_URI

        oauth=OAuthQQ(client_id=appid,client_secret=appkey,redirect_uri=redirect_uri,state=next)

        #生成qq登录扫描链接地址
        login_url=oauth.get_qq_url()

        #响应
        return JsonResponse({'code': '0','errmsg': 'ok','login_url': login_url})



# from itsdangerous import URLSafeSerializer
# from itsdangerous import BadSignature
# # 密钥，用于生成签名
# secret_key = 'my-secret-key'
# serializer = URLSafeSerializer(secret_key)
#
# # 生成签名令牌
# data = {'user_id': 22222}
# token = serializer.dumps(data) ##'eyJ1c2VyX2lkIjoyMjIyMn0.QVSap7uQhQ4IfpzVE-XF0cSgdWY'
#
#
# # 验证签名令牌
# try:
#     data = serializer.loads(token)
#     user_id = data['user_id']
#     email = data['email']
# except BadSignature:
#     # 签名无效
#     user_id = None
#     email = None
