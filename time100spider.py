import os
import requests
from pyquery import PyQuery as pq

from utils import log


class Model():
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


'''
requests.get(url)可以直接向URL发送请求并接收数据，
获取的数据用.content转化成HTML文本，
这些数据还有通过pyquery()转化一次才能使用css选择器获取想要的内容。
'''


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.other = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


# 提供特定的标签，从这个标签中提取数据
def movie_from_div(li):
    # 对每个li读取数据
    e = pq(li)
    # 小作用域变量用单字符
    # 时光网页面逻辑四项分散，分别对四个div进行数据读取
    number = e('.number')
    mov_pic = e('.mov_pic')
    mov_con = e('.mov_con')
    mov_point = e('.mov_point')

    m = Movie()
    m.name = mov_pic('img').attr('alt').split('/', 0)
    m.other = mov_pic('img').attr('alt').split('/', 1)
    m.score = mov_point('.total').text() + mov_point('.total2').text()
    m.quote = mov_con('.mt3').text()
    m.cover_url = mov_pic('img').attr('src')
    m.ranking = number('em').text()
    return m


# 根据URL和网页文件名获取数据，判断是否在本地
def get(url, filename):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    # 建立 cached 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    # 验证是否已经有缓存
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def get_pic(url, filename):
    folder = 'pics'
    # 建立 pics 文件夹
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    # 验证是否已经有缓存
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求, 把结果写入到文件夹中, r.content是返回的数据，图片数据是二进制
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


# 读取保存的页面数据
def cached_page(url):
    # 判断是否是第一页，find函数找不到对象时会返回-1
    if url.find('-') != -1:
        filename = url.split('-', 1)[-1]
    else:
        filename = '1.html'
    log('缓存网页名', filename)
    page = get(url, filename)
    return page


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        get_pic(m.cover_url, filename)


# 获取URL的下的数据
def movies_from_url(url):
    page = cached_page(url)
    e = pq(page)
    ul = e("#asyncRatingRegion")
    lis = ul('li')
    log('获取的列表标签', ul)
    # log('lis test', lis, '\n', type(lis))
    # 调用 movie_from_div
    movies = [movie_from_div(i) for i in lis]
    log('movies', movies)
    save_cover(movies)
    return movies


# http://www.mtime.com/top/movie/top100/
# http://www.mtime.com/top/movie/top100/index-2.html
def main():
    for i in range(1, 11):
        if i == 1:
            url = 'http://www.mtime.com/top/movie/top100/'
        else:
            url = 'http://www.mtime.com/top/movie/top100/index-{}.html'.format(i)
        movies = movies_from_url(url)
        print('top100 movies', movies)


if __name__ == '__main__':
    main()
