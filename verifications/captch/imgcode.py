# 导入random模块
import random

# 导入Image,ImageDraw,ImageFont模块
from PIL import Image, ImageDraw, ImageFont, ImageFilter

chr_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
ttf_list = ['ALGER.TTF', 'ARIALNI.TTF', 'BRADHITC.TTF', 'CHILLER.TTF']

def rnd_chr(chr_list,chr_len):#生成随机字符
    return random.sample(chr_list, chr_len)

def rnd_font(font_list=ttf_list):#生成随机字体
    return random.choice(font_list)

def rnd_color():#生成随机色
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def check_code(width=120, height=40, chr_len=4, font_list=ttf_list, font_size=28):
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))  # 创建一个画布
    draw = ImageDraw.Draw(img, mode='RGB')
    code = rnd_chr(chr_list, chr_len)
    #写文字
    for i in range(chr_len):
        h = random.randint(0, 4)
        draw.text((i * width / chr_len, h), code[i], font=ImageFont.truetype(rnd_font(), font_size), fill=rnd_color())

    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rnd_color())

    # 写干扰圆圈
    for i in range(40):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=rnd_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rnd_color())

    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, round(width/10))
        y1 = random.randint(0, round(height/10))
        x2 = random.randint(0, round(width/10))
        y2 = random.randint(0, round(height/10))

        draw.line((x1, y1, x2, y2), fill=rnd_color())

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, ''.join(code)

if __name__ == '__main__':
    img, code = check_code()
    print(code) ##返回验证码文字和图片
    img.show()

    print(type(img))