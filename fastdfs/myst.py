from django.core.files.storage import Storage
from django.conf import settings
from goods.models import ImageStorage
import base64

#Django里的ImageField字段，不提供直接读取图片的方法，只将内容进行提取
##因此需要重写类，用于访问里边的路径进行图片领取
#因此这个字段下，一般存储为服务器的访问路径

class MyStorage(Storage):

    # def __init__(self, fdfs_base_url=None):
    #         self.fdfs_base_url=fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self,name,mode='rb'):
        #打开文件时会被调用的方法
        pass

    def _save(self,name,content):
        #保存文件时调用的
        pass

    def url(self, name):
        #返回文件的可访问全路径(服务器地址+图片存储位置)
        # return 'http:/'+name
        #读取ImageStorage模型中的image_data
        image=ImageStorage.objects.get(title=name)
        binary_data=image.image_data
        #将二进制编码为base64
        binary_data_base64 = base64.b64encode(binary_data).decode('utf-8')
        return binary_data_base64
