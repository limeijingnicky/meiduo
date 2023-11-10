from django.urls import path,re_path
from goods import views

app_name = 'goods'
urlpatterns = [
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/(?P<sort>.*)$', views.GoodsListView.as_view(), name='goodslist'),

]