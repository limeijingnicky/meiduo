from django.urls import path,re_path
from oauth import views


urlpatterns = [
    re_path(r'^qq/login/$', views.QQAuthURLView.as_view(),name='qqlogin'),
    re_path(r'^oauth_callback/$', views.QQAuthUserView.as_view(),name='qquser'),
]
