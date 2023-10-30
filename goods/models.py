from django.db import models
from users.utils import BaseModel



class GoodsCategory(BaseModel):
    """商品类别,自关联，类似于省市级的表"""
    name = models.CharField(max_length=20, verbose_name='商品类别名称')
    parent = models.ForeignKey('self', related_name='subs', null=True, blank=True, on_delete=models.CASCADE, verbose_name='商品父类别')

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannelGroup(BaseModel):
    """商品频道组"""
    name = models.CharField(max_length=20, verbose_name='频道组名')

    class Meta:
        db_table = 'tb_channel_group'
        verbose_name = '商品频道组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannel(BaseModel):
    """商品频道"""
    group = models.ForeignKey(GoodsChannelGroup,on_delete=models.CASCADE, verbose_name='频道组名')
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='一级商品类别')
    url = models.CharField(max_length=50, verbose_name='频道页面链接')
    sequence = models.IntegerField(verbose_name='组内顺序')

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = '商品频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name


class Brand(BaseModel):
    """品牌"""
    name = models.CharField(max_length=20, verbose_name='品牌名称')
    logo = models.ImageField(verbose_name='品牌图片')
    first_letter = models.CharField(max_length=1, verbose_name='品牌首字母')

    class Meta:
        db_table = 'tb_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SPU(BaseModel):
    """商品SPU"""
    name = models.CharField(max_length=50, verbose_name='spu名称')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name='品牌名称')
    category1 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat1_spu', verbose_name='一级类别名称')
    category2 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat2_spu', verbose_name='二级类别名称')
    category3 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat3_spu', verbose_name='三级类别名称')
    sales = models.IntegerField(default=0, verbose_name='spu销量')
    comments = models.IntegerField(default=0, verbose_name='spu评价数')
    desc_detail = models.TextField(default='', verbose_name='spu详细介绍')
    desc_pack = models.TextField(default='', verbose_name='spu包装信息')
    desc_service = models.TextField(default='', verbose_name='spu售后服务')

    class Meta:
        db_table = 'tb_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SKU(BaseModel):
    """商品SKU"""
    name = models.CharField(max_length=50, verbose_name='sku名称')
    caption = models.CharField(max_length=100, verbose_name='副标题')
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='spu名称')
    category = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='商品类别名称')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品单价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品进价')
    market_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品市场价')
    stock = models.IntegerField(default=0, verbose_name='商品库存')
    sales = models.IntegerField(default=0, verbose_name='商品销量')
    comments = models.IntegerField(default=0, verbose_name='商品评价数')
    is_launched = models.BooleanField(default=True, verbose_name='商品是否上架销售')
    default_image_url = models.CharField(max_length=200, default='', null=True, blank=True, verbose_name='商品默认图片')

    class Meta:
        db_table = 'tb_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class SKUImage(BaseModel):
    """SKU图片"""
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku名称')
    image = models.ImageField(verbose_name='商品图片')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.name, self.id)


class SPUSpecification(BaseModel):
    """商品SPU规格"""
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, related_name='specs', verbose_name='SPU名称')
    name = models.CharField(max_length=20, verbose_name='spu规格名称')

    class Meta:
        db_table = 'tb_spu_specification'
        verbose_name = '商品SPU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.name)


class SpecificationOption(BaseModel):
    """规格选项"""
    spec = models.ForeignKey(SPUSpecification, related_name='options', on_delete=models.CASCADE, verbose_name='spu规格名称')
    value = models.CharField(max_length=20, verbose_name='规格选项值')

    class Meta:
        db_table = 'tb_specification_option'
        verbose_name = '规格选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.spec, self.value)


class SKUSpecification(BaseModel):
    """SKU具体规格"""
    sku = models.ForeignKey(SKU, related_name='specs', on_delete=models.CASCADE, verbose_name='sku名称')
    spec = models.ForeignKey(SPUSpecification, on_delete=models.PROTECT, verbose_name='spu规格名称')
    option = models.ForeignKey(SpecificationOption, on_delete=models.PROTECT, verbose_name='规格选项')

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'SKU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s - %s' % (self.sku, self.spec.name, self.option.value)

