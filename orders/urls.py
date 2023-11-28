from django.urls import path,re_path
from orders import views

app_name = 'orders'
urlpatterns = [
    re_path(r'^orders/settlement/$', views.OrderSettlemnetView.as_view(), name='settlement'),
    re_path(r'^orders/commit/$', views.OrderCommitView.as_view(), name='commit'),
    re_path(r'^orders/success/$', views.OrderSuccessView.as_view(), name='success'),
]
