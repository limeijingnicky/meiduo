##自定义认证的后端，实现多账号登录
from django.contrib.auth.backends import ModelBackend
import re
from users.models import Users
from django.db import models



def get_user_by_account(accoun):
    account=str(accoun)
    # 校验username是用户名还是手机号码
    try:
        if re.match(r'^1\d{10}$', account):
            ##输入值为手机号
            user = Users.objects.get(mobile=account)
        else:
            ##输入值为用户名
            user = Users.objects.get(username=account)
    except Users.DoesNotExist:
        return None
    else:
        return user




class UsernameMobileBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            print("后台登录")
            #后台登录
            try:
                user=Users.objects.get(username=username,is_superuser=True)
            except:
                user=None
            if user and user.check_password(password):
                return user

        else:
            print("前端登录")
            #重写用户认证方法
            user=get_user_by_account(username)

            #使用账号或者电话查询用户是否存在,如果可以查询到用户，则需要校验密码是否正确
            if user and user.check_password(password):
                #返回user
                return user
            return None

class BaseModel(models.Model):
    create_time=models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    updata_time=models.DateTimeField(auto_now=True,verbose_name="更新时间")

    class Meta:
        abstract=True #抽象类，用于继承用，不会单独创建表


