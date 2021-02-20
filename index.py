"""
@Author: Jianxun
@Email: i@lijianxun.top
@File Name: index.py
@Description: 三晋先锋自动积分脚本

1. 支持腾讯云函数
2. 支持本地运行
3. 直接输入用户名和密码

"""
import base64
import json
import os
import sys
import time
from threading import Thread

from Crypto.Cipher import AES

import requests
from loguru import logger

# --------------------------------------------- #
# 存放用户名，密码，Server 酱 SCKEY
# 用户名和密码以列表形式存放，可提供多个账号
# 支持直接输入用户名和密码
# --------------------------------------------- #

SCKEY = ""

user_list = [
    {
        "username": os.environ.get('tel1'),
        "password": os.environ.get('pd1')
    }
]


class EncryptDate(object):
    """
    参考：https://github.com/RuikaiWang/Study/blob/master/PassWordEncode.py
    """

    def __init__(self):
        self.key = "sanjinxianfengya".encode("utf8")  # 初始化密钥
        self.length = AES.block_size  # 初始化数据块大小
        self.aes = AES.new(self.key, AES.MODE_ECB)  # 初始化AES,ECB模式的实例
        self.unpad = lambda date: date[0:-ord(date[-1])]

    def pad(self, text):
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext

    def encrypt(self, encrData):  # 加密函数
        res = self.aes.encrypt(self.pad(encrData).encode("utf8"))
        msg = str(base64.b64encode(res), encoding="utf8")
        return msg

    def decrypt(self, decrData):  # 解密函数
        res = base64.decodebytes(decrData.encode("utf8"))
        msg = self.aes.decrypt(res).decode("utf8")
        return self.unpad(msg)


class SJXF(object):

    __doc__ = "三晋先锋自动积分 腾讯云函数版本"

    def __init__(self):
        # --------------------------------------------- #
        # 基本配置
        # --------------------------------------------- #

        self.base_url = "http://221.204.170.88:8184/app/"
        self.telephone = ""
        self.auth = ""
        self.user_id = ""
        self.article_id = ""
        self.article = dict()
        self.auth_list = list()

        # --------------------------------------------- #
        # 各接口请求头
        # --------------------------------------------- #

        # 登录接口请求头
        self.login_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Content-Length": "133",
            "Host": "221.204.170.88:8184",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.8.0"
        }

        # 试听，阅读接口请求头
        self.normal_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self.auth,
            "sUserId": str(self.user_id),
            "Host": "221.204.170.88:8184",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.8.0"
        }

        # 点赞，收藏请求头
        self.like_collect_headers = {
            "Authorization": self.auth,
            "sUserId": str(self.user_id),
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": "48",
            "Host": "221.204.170.88:8184",
            "Connection": "close",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.10.0",
            "version": "3.3.4"
        }

        # 答题接口请求头
        self.question_headers = {
            "Authorization": self.auth,
            "sUserId": str(self.user_id),
            "Cache-Control": "no-cache",
            "Connection": "close",
            "Host": "221.204.170.88:8184",
            "Origin": "http://sxzhdjkhd.sxdygbjy.gov.cn:8081",
            "Pragma": "no-cache",
            "Referer": "http://sxzhdjkhd.sxdygbjy.gov.cn:8081/zhdj-pre/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045410 Mobile Safari/537.36",
            "X-Requested-With": "io.dcloud.H5B1841EE"
        }

        # 查询积分接口请求头
        self.score_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Authorization": self.auth,
            "sUserId": str(self.user_id),
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive",
            "Host": "221.204.170.88:8184",
            "Origin": "http://sxzhdjkhd.sxdygbjy.gov.cn:8081",
            "Pragma": "no-cache",
            "Referer": "http://sxzhdjkhd.sxdygbjy.gov.cn:8081/zhdj-pre/index.html",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045410 Mobile Safari/537.36",
            "X-Requested-With": "io.dcloud.H5B1841EE",
            "Content-Type": "application/json; charset=UTF-8",
            "Content-Length": "47"
        }

    # --------------------------------------------- #
    # 登录接口 : 1 分
    # --------------------------------------------- #

    def login(self, username, password):
        """获取登录积分"""

        data = {
            "clientid": "234234",
            "deviceId": "imei867391035223309",
            "password": password,
            "userName": username,
            "verifyCode": ""
        }

        url = self.base_url + "user/login"
        response = requests.post(
            url, headers=self.login_headers, json=data).json()
        user_auth_info = response["data"]
        info = json.loads(base64.b64decode(user_auth_info))
        auth, user_id = [info['jwtToken'], info['id']]
        logger.info(response["msg"])
        logger.debug("auth: {}".format(auth))
        logger.info("user_id: {}".format(user_id))
        return {"auth": auth, "user_id": user_id, "username": username}

    # --------------------------------------------- #
    # 阅读接口 : 3 分
    # --------------------------------------------- #

    def read(self):
        """获取阅读积分"""

        logger.info("阅读 35 秒")
        end_time = int(time.time())
        start_time = end_time - 35
        url = self.base_url + "businessScore"
        headers = self.normal_headers.copy()
        headers.update(
            {"Content-Length": "76", "Content-Type": "application/json; charset=utf-8"})
        data = {
            "userId": self.user_id,
            "time": 35,
            "type": "1",
            "articleId": self.article_id,
            "ifScore": 1,
            "appStartTime": start_time
        }
        response = requests.post(url, headers=headers, json=data).json()
        logger.debug(response)
        logger.info("阅读完成")

    # --------------------------------------------- #
    # 试听学习接口 : 3 分
    # --------------------------------------------- #

    def listen(self):
        """获取视听学习积分"""

        logger.info("观看 10 分钟")
        end_time = int(time.time())
        start_time = end_time - 600
        url = self.base_url + "businessScore"
        headers = self.normal_headers.copy()
        headers.update(
            {"Content-Length": "72", "Content-Type": "application/json; charset=utf-8"})
        data = {
            "userId": self.user_id,
            "time": 600,
            "type": "2",
            "articleId": "12",
            "ifScore": 1,
            "appStartTime": start_time
        }
        response = requests.post(url, headers=headers, json=data).json()
        logger.debug(response)
        logger.info("观看完成")

    # --------------------------------------------- #
    # 点赞收藏接口 : 2 分
    # --------------------------------------------- #

    def get_article_list(self):
        """获取「晋组动态」第一页文章列表"""

        url = self.base_url + "study/list_article/72?size=10&page=1"
        headers = self.like_collect_headers.copy()
        headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        del headers["Content-Length"]
        logger.debug("正在获取文章列表")
        response = requests.get(url, headers=headers).json()

        for article in response["data"]:
            self.article.update({str(article["id"]): article["title"]})

    def req(self, url, article_id):
        """点赞/取消点赞；收藏/取消收藏统一请求"""

        time.sleep(2)
        _data = {"userId": int(self.user_id), "uniqueId": article_id, "type": "1"}
        logger.debug(_data)
        response = requests.post(
            url, headers=self.like_collect_headers, json=_data).json()
        logger.debug(response)
        return response

    def cancel_like(self, article_id):
        """取消点赞"""

        url = self.base_url + "loveCancelDelete"
        logger.info("取消点赞 - {}".format(self.article[article_id]))
        self.req(url=url, article_id=article_id)

    def cancel_collect(self, article_id):
        """取消收藏"""

        url = self.base_url + "collectCancelDelete"
        logger.info("取消收藏 - {}".format(self.article[article_id]))
        self.req(url=url, article_id=article_id)

    def like(self, article_id):
        """点赞文章"""

        url = self.base_url + "love"
        logger.info("点赞 - {}".format(self.article[article_id]))
        self.req(url=url, article_id=article_id)

    def collect(self, article_id):
        """收藏文章"""

        url = self.base_url + "collect"
        logger.info("收藏 - {}".format(self.article[article_id]))
        self.req(url=url, article_id=article_id)

    def do_like_collect(self, article_id, _data):
        """
        通过查询文章是否点赞或收藏，对应操作
        如果文章已点赞，则取消点赞并再次点赞
        如果文章未点赞，则点赞
        收藏亦然
        """

        if _data["ifLove"]:
            logger.info("该文章已点赞 - {}".format(self.article[article_id]))
            self.cancel_like(article_id)
            time.sleep(2)
            self.like(article_id)
        else:
            self.like(article_id)

        if _data["ifCollect"]:
            logger.info("该文章已收藏 - {}".format(self.article[article_id]))
            self.cancel_collect(article_id)
            time.sleep(2)
            self.collect(article_id)
        else:
            self.collect(article_id)

    def search_like_collect(self, article_id):
        """查询是否点赞或收藏"""

        url = self.base_url + "loveAndCollect"
        response = self.req(url=url, article_id=article_id)
        _data = response["data"]
        return _data

    def like_collect_main(self):
        """点赞和收藏的主程序"""

        self.get_article_list()

        # 看视频
        self.listen()

        for article_id in list(self.article)[2:4]:
            data = self.search_like_collect(str(article_id))
            self.do_like_collect(str(article_id), data)
            self.article_id = str(article_id)
            time.sleep(2)

            # 阅读
            self.read()
            time.sleep(2)

    # --------------------------------------------- #
    # 自学自测答题接口 : 6 分
    # --------------------------------------------- #

    def get_question_lib(self, q_type):
        """获取题库，并筛选出正确答案"""

        url = self.base_url + "questionLib"
        headers = self.question_headers.update({
            "Content-Length": "37",
            "Content-Type": "application/json",
        })
        _data = {"page": 1, "pageSize": 10, "themeId": q_type}
        logger.info("正在请求题库 -> {}，并整理正确答案".format(q_type))
        response = requests.post(url, json=_data, headers=headers).json()
        _result = [{"selectAnswer": data["correctAnswer"],
                    "grade": data["grade"],
                    "ifCorrect": 1,
                    "questionCode": data["code"],
                    "questionType": data["type"]}
                   for data in response["data"]["list"]]
        return _result

    def get_question_uuid(self):
        """获取 uuid"""

        url = self.base_url + "uuid"
        headers = self.question_headers.update({
            "Accept": "* / *",
            "Accept-Encodin": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        })
        logger.info("正在获取临时生成的 uuid")
        response = requests.get(url, headers=headers).json()
        if not response["success"]:
            logger.error("获取 uuid 失败！请求头:\n{}\n原始响应数据：\n{}".format(
                self.question_headers, response))
            sys.exit()
        logger.info("获取到 uuid：{}".format(response["data"]))
        return response["data"]

    def post_question(self, _t, _ty):
        """提交答案"""

        answer_list = self.get_question_lib(_t)
        _uuid = self.get_question_uuid()
        url = self.base_url + "question"
        headers = self.question_headers.update(
            {"Content-Type": "application/json", })
        _data = {
            "method": _ty,
            "summaryCode": _uuid,
            "totalGrade": "100",
            "userId": str(self.user_id),
            "list": answer_list
        }
        response = requests.post(url, headers=headers, json=_data).json()
        if not response["success"]:
           logger.error("请求失败，返回数据：{}".format(response))

    def question_main(self):
        """自学自测主程序"""

        question_type = ["3", "4", "", ""]
        ty = [4, 4, 1, 1]
        for _t, _ty in zip(question_type, ty):
            self.post_question(_t, _ty)
            time.sleep(3)

    # --------------------------------------------- #
    # 积分查询接口
    # --------------------------------------------- #

    def get_score(self):
        """总分查询接口"""

        url = self.base_url + "home/totayScore"
        data = {"userId": str(self.user_id), "deptId": "", "type": 2}
        response = requests.post(
            url, headers=self.score_headers, json=data).json()
        today_score = response["data"]["todayScore"]
        self.year_score = response["data"]["yearScore"]
        self.title = "{} 今日获取成绩：{}".format(self.telephone, today_score)
        logger.info(self.title)

    def score_detail(self):
        """分数详情"""

        url = self.base_url + \
            "personalCenter/getNoDailyTask?userId={}".format(self.user_id)
        headers = self.score_headers.copy()
        headers.update({"Connection": "close", "version": "3.3.4"})
        del headers["Content-Length"]
        del headers["Content-Type"]
        response = requests.get(url, headers=headers).json()
        data = response["data"]
        message = list()
        message.append("#### 本年度总成绩：{}\n".format(self.year_score))
        for info in data:
            msg = "- {}: {}\n".format(info["name"], info["yetScore"])
            message.append(msg)
        self.content = "\n".join(message)

    def send_msg(self, key):
        """使用 server 酱通知到微信"""

        url = "https://sc.ftqq.com/{}.send".format(key)
        time.sleep(5)
        data = requests.get(url, params={
            "text": self.title, "desp": self.content}).json()
        if data['errno'] == 0:
            logger.info('用户:' + self.telephone + '  Server酱推送成功')
        else:
            logger.error('用户:' + self.telephone + '  Server酱推送失败,请检查sckey是否正确')

    def score_main(self, telephone):
        self.telephone = telephone
        self.get_score()
        self.score_detail()

        if SCKEY:
            self.send_msg(key=SCKEY)

    # --------------------------------------------- #
    # 三晋先锋运行主程序
    # --------------------------------------------- #

    def main(self, user):

        secret_code = EncryptDate()
        user_info = self.login(username=user["username"],
                               password=secret_code.encrypt(user["password"]))
        logger.info("正在执行账号：{}".format(user_info["username"]))
        self.auth = user_info["auth"]
        self.user_id = user_info["user_id"]
        self.like_collect_main()  # 点赞收藏
        self.question_main()  # 自学自测
        self.score_main(telephone=user_info["username"])  # 积分查询


def main_handler(e, h):
    tasks = list()

    for user in user_list:
        s = SJXF()
        t = Thread(target=s.main, args=(user,))
        tasks.append(t)

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


if __name__ == '__main__':
    main_handler("", "")
