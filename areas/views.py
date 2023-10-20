from django.shortcuts import render
from django.views import View
from areas.models import Area
from django.http import JsonResponse

class AreasView(View):
    #使用get方法，传area_id,代表地区数据id
    def get(self,request):
        area_id = request.GET.get('area_id')
        if not area_id:

            try:
                #需要查询省份
                province_models=Area.objects.filter(parent__isnull=True)
                # return render(request,'user_center_site.html') ##可以直接渲染到网页上
                #需要模型列表转为字典
                province_models_list=[]
                for province_model in province_models:
                    p = {
                        'id':  province_model.id,
                        'name': province_model.name
                    }
                    province_models_list.append(p)
                return JsonResponse({'code': 0,'errmsg':'ok','province_list':province_models_list}) #将所有省级名称数据传入页面
            except Exception as e:
                return JsonResponse({'code': 408,'errmsg':'查询省份错误'})

        if area_id:
            #需要查询地区数据
            pass


