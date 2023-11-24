from django.urls import path,re_path
from goods import views

app_name = 'goods'
urlpatterns = [
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/(?P<sort>.*)$', views.GoodsListView.as_view(), name='goodslist'),
    re_path(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(),name='detail'),
    re_path(r'^hot/(?P<category_id>\d+)/$',views.HotView.as_view(),name='hot'),
    re_path(r'^detail/visit/(?P<category_id>\d+)/$',views.DetailVisitView.as_view(),name='visit_count'),
]

