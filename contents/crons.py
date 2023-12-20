from contents.views import get_categories
from collections import OrderedDict
from contents.models import ContentCategory
from django.shortcuts import render
from django.template import loader

def generate_static_index_html():
    #静态化页面
    """提供首页广告界面"""
    category_data = get_categories()

    ##查询广告数据
    contents = OrderedDict()
    content_categories = ContentCategory.objects.all()
    for content_categorie in content_categories:
        contents[content_categorie.key] = content_categorie.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': category_data,
        'contents': contents
    }

    template=loader.get_template('index.html')
    html_text_template = template.render(context)
    with open('../static/indexs/index.html','w',encoding='utf-8') as f:
        f.write(html_text_template)

    return 'ok'
