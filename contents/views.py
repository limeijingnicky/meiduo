import json
from django.shortcuts import render
from django.views import View
from goods.models import GoodsChannelGroup,GoodsChannel,GoodsCategory
from collections import OrderedDict
from django.http import JsonResponse,HttpResponse
from contents.models import Content,ContentCategory


def get_categories():
    # 查询商品频道和分类
    channels = GoodsChannel.objects.all().order_by('group_id', 'sequence')
    category_data = []

    for channel in channels:
        group_id = channel.group_id

        if not category_data or category_data[-1]['group_id'] != group_id:
            category_data.append({
                'group_id': group_id,
                'channels': [],
                'sub_cats': []
            })

        cat1 = channel.category
        category_data[-1]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })

        for cat2 in cat1.subs.all():
            cat2_data = {
                'id': cat2.id,
                'name': cat2.name,
                'sub_cats': []
            }
            for cat3 in cat2.subs.all():
                cat2_data['sub_cats'].append({
                    'id': cat3.id,
                    'name': cat3.name
                })
            category_data[-1]['sub_cats'].append(cat2_data)

    return category_data


class IndexView(View):

    def get(self, request):
        """提供首页广告界面"""
        category_data=get_categories()

        ##查询广告数据
        contents=OrderedDict()
        content_categories=ContentCategory.objects.all()
        for content_categorie in content_categories:
            contents[content_categorie.key]=content_categorie.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': category_data,
            'contents': contents
        }

        return render(request,'index.html',context=context)



