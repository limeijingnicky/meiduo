from haystack import indexes
from .models import SKU

class SKUIndex(indexes.SearchIndex,indexes.Indexable):
    '''SKU索引数据模型类'''
    #接收索引字段：使用文档定义索引字段，并且使用模板语法渲染
    text = indexes.CharField(document=True,use_template=True)

    def get_model(self):
        return SKU

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)