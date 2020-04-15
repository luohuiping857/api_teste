"""
============================
Author:柠檬班-木森
Time:2020/3/24   20:49
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
import os
import unittest
import random
from common.handle_excel import HandleExcel
from library.myddt import ddt, data
from common.handle_config import conf
from requests import request
from common.handle_logging import log
from common.handle_path import DATA_DIR
from common.handle_db import HandleMysql

filename = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class RegisterTestCase(unittest.TestCase):
    excel = HandleExcel(filename, "register")
    cases = excel.read_data()
    db = HandleMysql()

    @data(*cases)
    def test_register(self, case):
        # 第一步：准备用例数据
        # 请求方法
        method = case["method"]
        # 请求地址
        url = case["url"]
        # 请求参数
        # 判断是否有手机号码需要替换
        if "#phone#" in case["data"]:
            # 随机生成一个手机号码
            phone = self.random_phone()
            # 将参数中的#phone# 替换成随机生成的手机号
            case["data"] = case["data"].replace("#phone#",phone)
        data = eval(case["data"])
        # 请求头
        headers = eval(conf.get("env", "headers"))
        # 预期结果
        expected = eval(case["expected"])
        # 用例所在行
        row = case["case_id"] + 1

        # 第二步：发送请求获取实际结果
        response = request(method=method, url=url, json=data, headers=headers)
        # 获取实际结果
        res = response.json()
        print("预期结果：", expected)
        print("实际结果：", res)

        # 第三步：断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 判断是否需要进行sql校验
            if case["check_sql"]:
                sql = case["check_sql"].replace("#phone#",data["mobile_phone"])
                res = self.db.find_count(sql)
                self.assertEqual(1, res)
        except AssertionError as e:
            # 结果回写excel中
            log.error("用例--{}--执行未通过".format(case["title"]))
            log.debug("预期结果：{}".format(expected))
            log.debug("实际结果：{}".format(res))
            log.exception(e)
            self.excel.write_data(row=row, column=8, value="未通过")
            raise e
        else:
            # 结果回写excel中
            log.info("用例--{}--执行通过".format(case["title"]))
            self.excel.write_data(row=row, column=8, value="通过")

    @classmethod
    def random_phone(cls):
        """生成一个数据库里面未注册的手机号码"""
        while True:
            phone = "155"
            for i in range(8):
                r = random.randint(0, 9)
                phone += str(r)

            # 数据库中查询该手机号是否存在
            sql = "SELECT * FROM futureloan.member WHERE mobile_phone={}".format(phone)
            res = cls.db.find_count(sql)
            # 如果不存在，则返回该手机号
            if res == 0:
                return phone
