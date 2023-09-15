from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage

def environment(**options):
    # 创建环境对象
    # jinja2环境
    env = Environment(**options)


    # 2.将自定义的过滤器添加到 环境中
    env.filters['do_listreverse'] = do_listreverse
    env.filters['do_length'] = do_length


    # 自定义语法
    env.globals.update({
        'url': 'reverse',  ##在模板内做重定向
        # 'static': staticfiles_storage.url  ##获取静态文件夹的存储位置
    })

    return env



# 1.自定义过滤器
def do_listreverse(li):
    if li == "B":
        return "哈哈"
#
# 2.自定义过滤器
def do_length(lii):
    if len(lii) == 3:
        return "the lengh is 3"




