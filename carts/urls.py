from carts import views
from django.urls import path,re_path

urlpatterns = [
    re_path(r'^carts/$', views.CartsView.as_view()),
]