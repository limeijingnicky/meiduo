from django.shortcuts import render,redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.http import JsonResponse,HttpResponseForbidden,HttpResponseServerError
import logging
from oauth.models import OAuthQQUser
from django.contrib.auth import login
from itsdangerous import URLSafeSerializer
from itsdangerous import BadSignature


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
            # 当不存在时,关联已存在的用户名或者新建一个用户
            context={'openid': token}
            return render(request,'oauth_callback.html',context)

        else:
            #当存在时
            login(request,oauth_user.user)

            response = redirect('/')
            response.set_cookie('username',oauth_user.user.username,max_age=3600*24*15)

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
