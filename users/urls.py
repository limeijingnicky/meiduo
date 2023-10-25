from users import views
from django.urls import path,re_path


urlpatterns = [
    path(r'register/', views.RegisterView.as_view()),
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    re_path(r'^mobiles/(?P<mobile>1[0-9]\d{9})/count/$', views.MobileCountView.as_view()),
    re_path(r'^login/', views.LoginView.as_view(),name='login'),
    re_path(r'^logout/', views.LogoutView.as_view(),name='logout'),
    re_path(r'^info/', views.UserinfoView.as_view(), name='info'),
    re_path(r'^cart/', views.UserCartView.as_view(), name='cart'),
    re_path(r'^order/', views.UserOrderView.as_view(), name='order'),
    re_path(r'^emails/', views.EmailView.as_view(), name='email'),
    re_path(r'^verification/$', views.VerifyEmailView.as_view(), name='verify_email'),
    re_path(r'^address/$', views.AddressView.as_view(), name='address'),
    re_path(r'^addresses/create/$', views.AddressCreateView.as_view(), name='address_create'),
]