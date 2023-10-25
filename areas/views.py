from django.shortcuts import render
from django.views import View
from areas.models import Area
from django.http import JsonResponse
from django.core.cache import cache


class AreasView(View):
    #使用get方法，传area_id,代表地区数据id
    def get(self,request):
        area_id = request.GET.get('area_id')

        if not area_id:
            #获取缓存数据
            province_models_list=cache.get('province_model_list')

            if not province_models_list:
                #需要查询省份
                try:
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
                    #将自动加载的省份数据，进行缓存
                    cache.set('province_model_list',province_models_list,3600)

                except Exception as e:
                    return JsonResponse({'code': 408,'errmsg':'查询省份错误'})

            return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_models_list})  # 将所有省级名称数据传入页面
        ##先通过省的id，查找下级市和市区
        # 多查一时：子集.外键（可以查到主键）
        # 一查多时：主键.关联子集（可以查到关联子集）
        if area_id:

            # 获取缓存数据
            sub_data= cache.get('sub_area_'+area_id)

            if not sub_data:
                try:
                    #先通过省的area_id，确定对象
                    parent_model=Area.objects.get(id=area_id)
                    #通过模型的related关系 获得下级对象
                    # sub_model=sheng_model.area_set.all()
                    sub_model= parent_model.subs.all()

                    subs=[]
                    for sub in sub_model:
                        sub_dict={
                            'id':sub.id,
                            'name': sub.name
                        }
                        subs.append(sub_dict)

                    sub_data={
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs
                    }

                    #缓存城市或区县
                    cache.set('sub_area_'+area_id,sub_data,3600)

                except Exception as e:
                    return JsonResponse({
                        'code': 409,
                        'errmsg': '查询城市或区县错误',
                    })

            else:
                return JsonResponse({
                    'code':0,
                    'errmsg':'ok',
                    'sub_data': sub_data
                })



