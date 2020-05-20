
import requests
import re
import time
import random
import numpy as np

class WenJuanXing:
    def __init__(self, url):
        """
        :param url:要填写的问卷的url
        """
        self.wj_url = url
        self.post_url = None
        self.header = None
        self.cookie = None
        self.data_input()

    def set_data(self):
        """
        这个函数中生成问卷的结果，
        :return:
        """
        sumbitdata = ""
        for index in range(23):
            if self.wjdata[index][0] == 0:
                for i, num in enumerate(self.wjdata[index]):
                    if i != 0:
                        if num > 0:
                            self.wjdata[index][i] -= 1
                            sumbitdata += '{}${}}}'.format(index+1,i)
                            break
            else:
                multiChoice = []
                for i, num in enumerate(self.wjdata[index]):
                    if i != 0:
                        if num > 0:
                            self.wjdata[index][i] -= 1
                            multiChoice.append(i)
                s =np.array(self.wjdata[index]).sum()
                offset = (np.array(self.wjdata[index]).sum() - 1) - self.wjNumber
                if offset < 0:
                    self.wjdata[index][np.argmax(self.wjdata[index])] -= offset
                    self.wjdata[index][0] = 0
                sumbitdata += '{}$'.format(index+1)
                for choice in multiChoice:
                    sumbitdata += '{}|'.format(choice)
                sumbitdata = sumbitdata[:-1]
                sumbitdata += '}'
        sumbitdata = sumbitdata[:-1]
        self.wjNumber -= 1
        data={
            'submitdata': sumbitdata
        }
        return data

    def  data_input(self):
        """
        这个函数用于录入自定义数据分布
        rowIndex =0 上的0、1分别代表单选和多选
        :return:
        """
        self.wjdata = np.array([[0,164,136],
                       [0,40,100,60,53,27,20],
                       [0,37,200,63],
                       [0,47,153,100],
                       [0,278,22],
                       [0,189,111],
                       [0,11,136,150,3],
                       [0,118,122,38,22],
                       [1,48,72,212,42,11,83,15],
                       [1,109,47,218,103,11],
                       [0,234,46,20],
                       [1,199,145,136,88,107,212,74,16],
                       [0,49,121,130],
                       [1,75,183,225,184,103,22],
                       [0,74,186,37,3],
                       [0,72,96,118,14],
                       [0,31,243,26],
                       [1,223,257,123,215,268],
                       [0,11,101,124,64],
                       [0,250,9,41],
                       [0,193,23,81,3],
                       [0,164,136],
                       [0,227,45,1,27]])
        self.wjNumber = 300


    def set_header(self):
        """
        随机生成ip，设置X-Forwarded-For
        ip需要控制ip段，不然生成的大部分是国外的
        :return:
        """
        ip = '{}.{}.{}.{}'.format(112, random.randint(64, 68), random.randint(0, 255), random.randint(0, 255))
        self.header = {
            'X-Forwarded-For': ip,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko\
                        ) Chrome/71.0.3578.98 Safari/537.36',
        }

    def get_ktimes(self):
        """
        随机生成一个ktimes,ktimes是构造post_url需要的参数，为一个整数
        :return:
        """
        return random.randint(15, 50)

    def get_response(self):
        """
        访问问卷网页，获取网页代码
        :return: get请求返回的response
        """
        response = requests.get(url=self.wj_url, headers=self.header)
        self.cookie = response.cookies


        return response

    def get_jqnonce(self, response):
        """
        通过正则表达式找出jqnonce,jqnonce是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的jqnonce
        """
        jqnonce = re.search(r'.{8}-.{4}-.{4}-.{4}-.{12}', response.text)
        return jqnonce.group()

    def get_rn(self, response):
        """
        通过正则表达式找出rn,rn是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的rn
        """
        rn = re.search(r'\d{9,10}\.\d{8}', response.text)
        return rn.group()

    def get_id(self, response):
        """
        通过正则表达式找出问卷id,问卷是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的问卷id
        """
        id = re.search(r'\d{8}', response.text)
        return id.group()

    def get_jqsign(self, ktimes, jqnonce):
        """
        通过ktimes和jqnonce计算jqsign,jqsign是构造post_url需要的参数
        :param ktimes: ktimes
        :param jqnonce: jqnonce
        :return: 生成的jqsign
        """
        result = []
        b = ktimes % 10
        if b == 0:
            b = 1
        for char in list(jqnonce):
            f = ord(char) ^ b
            result.append(chr(f))
        return ''.join(result)

    def get_start_time(self, response):
        """
        通过正则表达式找出问卷starttime,问卷是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的starttime
        """
        start_time = re.search(r'\d+?/\d+?/\d+?\s\d+?:\d{2}', response.text)
        return start_time.group()

    def set_post_url(self):
        """
        生成post_url
        :return:
        """
        self.set_header()  # 设置请求头，更换ip
        response = self.get_response()  # 访问问卷网页，获取response
        ktimes = self.get_ktimes()  # 获取ktimes
        jqnonce = self.get_jqnonce(response)  # 获取jqnonce
        rn = self.get_rn(response)  # 获取rn
        id = self.get_id(response)  # 获取问卷id
        jqsign = self.get_jqsign(ktimes, jqnonce)  # 生成jqsign
        start_time = self.get_start_time(response)  # 获取starttime
        time_stamp = '{}{}'.format(int(time.time()), random.randint(100, 200))  # 生成一个时间戳，最后三位为随机数
        url = 'https://www.wjx.cn/joinnew/processjq.ashx?submittype=1&curID={}&t={}&starttim' \
              'e={}&ktimes={}&rn={}&jqnonce={}&jqsign={}'.format(id, time_stamp, start_time, ktimes, rn, jqnonce, jqsign)
        self.post_url = url  # 设置url
        print(self.post_url)

    def post_data(self):
        """
        发送数据给服务器
        :return: 服务器返回的结果
        """
        response = requests.post(url=self.post_url, data=self.set_data(), headers=self.header, cookies=self.cookie)
        return response

    def run(self):
        """
        填写一次问卷
        :return:
        """
        self.set_post_url()
        result = self.post_data()
        print(result.content.decode())

    def mul_run(self, n):
        """
        填写多次问卷
        :return:
        """
        for i in range(n):
            time.sleep(random.randint(3,12))
            self.run()
            print("已提交总数"+str(i)+"\n")


if __name__ == '__main__':
    w = WenJuanXing('https://www.wjx.cn/jq/78271617.aspx')
    w.mul_run(300)


