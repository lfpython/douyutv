# coding=utf-8

import requests
import json
from lxml import etree
from queue import Queue
from threading import Thread
class Douyu(object):
    def __init__(self):
        self.start_url = "http://capi.douyucdn.cn/api/v1/getVerticalRoom?limit=100&offset={}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"
        }
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.content_list_queue = Queue()
        self.img_url_list_queue = Queue()


    def _parse_url(self,url):
        response = requests.get(url,headers=self.headers,timeout=5)
        assert response.status_code == 200
        return response.content.decode()

    def parse_url(self):
        while True:
            url = self.url_queue.get()
            try:
                html = self._parse_url(url)
            except Exception as e:
                html = None
            self.html_queue.put(html)
            self.url_queue.task_done()

    def get_url_list(self):
        # url_list = []
        for i in range(100):
            self.url_queue.put(self.start_url.format(i))
            # url_list.append(url)
        # return url_list

    def get_content_list(self):
        while True:
            html = self.html_queue.get()

            if html is not None:
                json_str = json.loads(html)
                data_list = json_str["data"]
                # print data_list
                content_list = []
                img_list = []
                for data in data_list:
                    # print data['nickname']
                    temp = {}
                    img = {}
                    
                    temp['nickname'] = data['nickname']     # 昵称
                    img['nickname'] = data['nickname']      # 昵称
                    temp['online'] = data['online']         # 在线
                    temp['img_url'] = data['vertical_src']      # 头像
                    img['img_url'] = data['vertical_src']
                    temp['uid'] = data['owner_uid']         # 账户
                    content_list.append(temp)
                    img_list.append(img)
                    # print content_list
                self.content_list_queue.put(content_list)
                self.img_url_list_queue.put(img_list)
            self.html_queue.task_done()

    def save_content(self):
        while True:
            content_list = self.content_list_queue.get()

            with open("douyu.json", "a",encoding='utf8') as f:
                for content in content_list:
                    # print(content)
                    # img_pic = requests.get(content['img_url'])
                    f.write(json.dumps(content,indent=2,ensure_ascii=False))
                    f.write(",")
                    f.write("\n")
            print('success_text')
            self.content_list_queue.task_done()


    def save_img(self):
        n = 0
        while True:
            img_list = self.img_url_list_queue.get()
            # with open("../爬虫数据/"+ str(name) + ".jpg","wb") as f:
            #     for content in content_list:
            #         img_src = requests.get(content["img_url"])
            #         f.write(img_src.content)
            # name_list = []
            for img in img_list:
                img_src = requests.get(img['img_url'])
                name = img['nickname']
                # name_list.append(name)
                with open("../爬虫数据/" + str(n) +"."+ str(name) + ".jpg", "wb") as f:
                    f.write(img_src.content)
                    print('success')
                    n +=1
            self.img_url_list_queue.task_done()

    def run(self):
        threading_list = []
        # 获取起始url
        t_url = Thread(target=self.get_url_list)
        threading_list.append(t_url)
        # print url_list
        # 发送请求，接收数据
        for i in range(10):
            t_parse = Thread(target=self.parse_url)
            threading_list.append(t_parse)
        # print json_str
        # 筛选数据，
        for i in range(10):
            t_content = Thread(target=self.get_content_list)
            threading_list.append(t_content)
        # 保存数据
        t_save_content = Thread(target=self.save_content)
        threading_list.append(t_save_content)
        # t_save_img = Thread(target=self.save_img)
        # threading_list.append(t_save_img)
        for t in threading_list:
            t.setDaemon(True)
            t.start()
        for q in [self.url_queue, self.html_queue, self.content_list_queue]:
            q.join()
            print(1111111111111)


if __name__ == '__main__':
    a = Douyu()
    a.run()