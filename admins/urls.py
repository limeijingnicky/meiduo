from django.urls import path,re_path
from admins.views.login_admins import *
from admins.views.home_admins import *
from rest_framework_jwt.views import obtain_jwt_token
from admins.views.statistical import UserCountView,UserIncreaseView,UserActiveView,UserOrderView,UserMonthView,GoodsVistView
from admins.views.user import UsersView,UserAddView
from admins.views.spec import SpecsView,SpecsAddView,SpecsDeleteView
from admins.views.spu import SpusView,SpusAddView,SpusDeleteView
from admins.views.category import CategoryGetView,CategoryAddView,CategoryView
from admins.views.brand import BrandGetView
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

    re_path(r'^user/(?P<page_num>\d+)/(?P<keyword>[a-zA-Z0-9_-]{0,20}$)', UsersView.as_view(), name='user_admins'),
    re_path(r'^add_user/$', UserAddView.as_view(), name='add_admins'),

    re_path(r'^specs/(?P<page_num>\d+)/(?P<keyword>[a-zA-Z0-9_-]{0,20}$)', SpecsView.as_view(), name='specs_admins'),
    re_path(r'^add_spec/$', SpecsAddView.as_view(), name='add_spec_admins'),
    re_path(r'^delete_spec/$', SpecsDeleteView.as_view(), name='delete_spec_admins'),

    re_path(r'^spus/(?P<page_num>\d+)/(?P<keyword>[a-zA-Z0-9_-]{0,20}$)', SpusView.as_view(), name='spus_admins'),
    re_path(r'^add_spu/$', SpusAddView.as_view(), name='add_spu_admins'),
    re_path(r'^delete_spu/$', SpusDeleteView.as_view(), name='delete_spu_admins'),

    re_path(r'^brands/$', BrandGetView.as_view(), name='brand_admins'),

    re_path(r'^categories/$', CategoryGetView.as_view(), name='category_admins'),
    re_path(r'^category/(?P<page_num>\d+)/(?P<keyword>[a-zA-Z0-9_-]{0,20}$)', CategoryView.as_view(), name='categories_admins'),
    re_path(r'^add_category/$', CategoryAddView.as_view(), name='add_category_admins'),

]
