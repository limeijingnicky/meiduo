import sys
sys.path.insert(0,'../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo.settings'
import django
django.setup()


from django.template import loader
from django.conf import settings
from goods import models
from goods.views import get_categories
from  goods.views import breadcrumb

def generate_static_sku_index_html(sku_id):
    #静态化页面
    sku = models.SKU.objects.get(id=sku_id)

     # 插入商品分类导航
    category = get_categories()

    # 插入面包屑导航栏
    breadc = breadcrumb(sku.category)

    spu = sku.spu
    sku_specs = spu.specs.filter(spu=spu)

    goods_specs = {}
    for sku_spec in sku_specs:
        value = []
        options = sku.specs.filter(spec=sku_spec)
        for option in options:
            value.append(option.option)
        goods_specs[sku_spec.name] = value

    # 查询sku
    context = {
        'category': category,
        'breadcrumb': breadc,
        'sku': sku,
        'specs': goods_specs,
    }


    template=loader.get_template('detail.html')
    html_text_template = template.render(context)
    with open(f'../static/indexs/{sku_id}.html','w',encoding='utf-8') as f:
        f.write(html_text_template)

    return sku_id

if __name__=='__main__':
    skus=models.SKU.objects.all()
    for sku in skus:
        generate_static_sku_index_html(sku.id)