"""
============================
Author:柠檬班-木森
Time:2020/4/7   20:45
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
import os
import jsonpath
import unittest
from library.myddt import ddt, data
from requests import request
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_data import replace_data, EnvData
from common.handle_logging import log

filename = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestInvest(unittest.TestCase):
    excel = HandleExcel(filename, "invest")
    cases = excel.read_data()

    @data(*cases)
    def test_invest(self, case):
        """投资用例"""
        # 第一步：准备数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        headers = eval(conf.get("env", "headers"))
        if case["interface"] != "login":
            # 如果不是登录接口，则添加一个token
            headers["Authorization"] = getattr(EnvData, "token")
        data = eval(replace_data(case["data"]))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取实际结果
        response = request(url=url, method=method, json=data, headers=headers)
        res = response.json()
        if case["interface"] == "login":
            # 如果是登录接口则提取用户id和token
            member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            token = "Bearer" + " " + jsonpath.jsonpath(res, "$..token")[0]
            setattr(EnvData, "member_id", member_id)
            setattr(EnvData, "token", token)
        if case["interface"] == "add":
            # 如果是加标接口则提取标id进行保存
            loan_id = str(jsonpath.jsonpath(res, "$..id")[0])
            setattr(EnvData, "loan_id", loan_id)
        # 第三步：断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
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


"""
投资接口的前置条件：
1、有可以投资的项目：
    创建一个项目（普通用户登录：借款人）：2个请求
        
    审核通过（管理员登录）：2个请求


2、用户要有钱：
    - 投资人（普通用户）登录：1个请求
    - 投资人充值：1个请求

执行投资相关的用例





"""


