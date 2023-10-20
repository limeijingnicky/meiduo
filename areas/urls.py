from django.urls import path,re_path
from areas import views


urlpatterns = [
    re_path(r'^areas/$', views.AreasView.as_view(), name='areas'),
]
