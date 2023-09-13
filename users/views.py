from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

# Create your views here.
class RegisterView(View):
    #用户注册
    def get(self,request):
        # return HttpResponse('it is ok')
        return render(request,'register.html')
