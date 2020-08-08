import re
import requests
from urllib import error
import os
from time import sleep

# 图片编号
num = 1
# 每个关键词要获取的图片数量
num_picture = 0
# 图片文件名初始化（总文件夹名）
kw_file = ''
# 图片URL列表
pic_url_list = []
# 图片文件夹编号
dir_num = []


def search_pics(original_url):
    """检测url有多少张图片可以爬"""
    global pic_url_list
    print("\n正在检测图片总数，请稍等.....")
    t = 0
    total_pic_num = 0
    while t < 1000:
        modified_url = original_url + str(t)
        try:
            # connect时间为7，read时间为20
            response = requests.get(modified_url, timeout=(7, 10))
        except error.HTTPError:
            t = t + 60
            print("网络错误，请调整网络后重试")
            continue
        else:
            rt = response.text
            # 先利用正则表达式找到图片url
            pic_url = re.findall('"objURL":"(.*?)",', rt, re.S)
            total_pic_num += len(pic_url)
            if len(pic_url) == 0:
                break
            else:
                pic_url_list.append(pic_url)
                t = t + 60
    return total_pic_num


def download_pic(html, keyword):
    """下载图片并保存至指定文件夹"""
    global num
    global each_num
    # 先利用正则表达式找到图片url
    pic_url = re.findall('"objURL":"(.*?)",', html, re.S)
    print("找到关键词\"" + keyword + "\"的图片，即将开始下载图片...")

    for each in pic_url:
        print("正在下载第" + str(num) + "张图片，图片地址:" + str(each))
        try:
            if each is not None:
                pic = requests.get(each, timeout=(7, 10))
                # sleep(1)
            else:
                continue
        except:
            print("错误，当前图片无法下载")
            continue
        else:
            file_name = kw_file + r'/' + keyword + '_' + str(num % each_num + 1) + '.jpg'
            with open(file_name, 'wb') as fp:
                fp.write(pic.content)
            num += 1

        if num > num_picture:
            return


if __name__ == '__main__':
    """
    主函数：对keywords.txt文件中每行的关键词，在百度图片上进行图片爬取并下载至本地
    """
    each_num = int(input("请输入每个关键词的图片的下载数量："))
    num_picture = each_num
    keyword_list = []

    with open('./keywords.txt', encoding='utf-8') as kw_file:
        # 获取文本文件中每一行关键字，用 strip()移除末尾的空格
        keyword_list = [kw.strip() for kw in kw_file.readlines()]
        for i in range(len(keyword_list)):
            dir_num.append(int(1))

    for keyword in keyword_list:
        url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + keyword + '&pn='
        total_num = search_pics(url)
        print("经检测有关\"%s\"的图片共有%d张" % (keyword, total_num))

        kw_file = keyword + '_images' + str(dir_num[keyword_list.index(keyword)])
        while os.path.exists(kw_file):
            print("该关键词的图片爬取过，将保存至新建文件夹...")
            dir_num[keyword_list.index(keyword)] += 1
            kw_file = keyword + '_images' + str(dir_num[keyword_list.index(keyword)])
        os.mkdir(kw_file)

        t = 0
        original_url = url
        while t < num_picture:
            try:
                modified_url = original_url + str(t)
                response = requests.get(modified_url, timeout=10)
                # print(modified_url)
            except error.HTTPError:
                print("网络错误，请调整网络后重试")
                t = t + 60
            else:
                download_pic(response.text, keyword)
                # sleep(0.5)
                t = t + 60

        num_picture += each_num

    print("\n指定图片爬取完成并分类存储！")
