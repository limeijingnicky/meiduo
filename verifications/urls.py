from django.urls import path,re_path
from verifications import views

urlpatterns = [
    ##利用get方法，传递imgcode的参数，例如uuid作为标识
   re_path(r'^register/image_codes/(?P<uuid>[\w-]+)/$',views.ImageCodeView.as_view()),
   re_path(r'^register/sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view())
]