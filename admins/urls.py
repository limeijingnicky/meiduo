from django.urls import path,re_path
from admins.views.login_admins import *
from admins.views.home_admins import *
from rest_framework_jwt.views import obtain_jwt_token
from admins.views.statistical import UserCountView,UserIncreaseView,UserActiveView,UserOrderView,UserMonthView,GoodsVistView

urlpatterns = [
    re_path(r'^authorizations/$', obtain_jwt_token, name='authorization'),
    re_path(r'^login/$',LoginAdminsView.as_view(), name='login_admins'),
    re_path(r'^home/$',HomeAdminsView.as_view(), name='home_admins'),
    re_path(r'^statistical/total_count/$', UserCountView.as_view(), name='count_admins'),
    re_path(r'^statistical/day_increment/$', UserIncreaseView.as_view(), name='increment_admins'),
    re_path(r'^statistical/day_active/$', UserActiveView.as_view(), name='active_admins'),
    re_path(r'^statistical/day_order/$', UserOrderView.as_view(), name='order_admins'),
    re_path(r'^statistical/month/$', UserMonthView.as_view(), name='month_admins'),
    re_path(r'^statistical/goodsvisit/$', GoodsVistView.as_view(), name='goodsvisit_admins'),
]
