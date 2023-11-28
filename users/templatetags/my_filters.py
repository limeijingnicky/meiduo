from django import template
register = template.Library()

#将手机号中间5位进行隐藏
@register.filter(name='hide_middle')
def hide_middle(value):
    if value and len(value)==11:
        new_v=value[0:3]+'*****'+value[8:11]
    return new_v

@register.filter(name='hide_middle_name')
def hide_middle_name(value):
    if value and len(value)>1:
        new_v=value[0]+'*'*(len(value)-2)+value[-1]
    return new_v