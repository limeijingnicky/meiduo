from django.shortcuts import render
from django.views import View
from areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache
from django.http import HttpResponse,JsonResponse
from rest_framework_jwt.views import obtain_jwt_token
from users.models import Users

class HomeAdminsView(View):
    def get(self,request):
        return render(request,'home_admins.html')
