from users import views
from django.urls import path,re_path


urlpatterns = [
    path(r'register/', views.RegisterView.as_view()),
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    re_path(r'^mobiles/(?P<mobile>1[0-9]\d{9})/count/$', views.MobileCountView.as_view()),
]