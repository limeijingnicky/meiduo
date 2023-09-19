from django.urls import path,re_path
from verifications import views

urlpatterns = [
    ##利用get方法，传递imgcode的参数，例如uuid作为标识
   re_path(r'^image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view())
]