"""
============================
Author:柠檬班-木森
Time:2020/3/31   20:47
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""

import os
import unittest
import jsonpath
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from library.myddt import ddt, data
from common.handle_config import conf
from requests import request
from common.handle_logging import log
from common.handle_db import HandleMysql


@ddt
class TestAudit(unittest.TestCase):
    excel = HandleExcel(os.path.join(DATA_DIR, "apicases.xlsx"), "audit")
    cases = excel.read_data()
    db = HandleMysql()

    @classmethod
    def setUpClass(cls):
        # 该用例类所有用例执行之前的前置条件：管理员要登录，普通用户登录
        url = conf.get("env", "url") + "/member/login"
        headers = eval(conf.get("env", "headers"))
        # 前置条件一：管理员登录
        admin_data = {
            "mobile_phone": conf.get("test_data", "admin_phone"),
            "pwd": conf.get("test_data", "admin_pwd")
        }
        response1 = request(method="post", url=url, json=admin_data, headers=headers)
        res1 = response1.json()
        # 提取管理员的token
        cls.admin_token = "Bearer" + " " + jsonpath.jsonpath(res1, "$..token")[0]

        # 前置条件二：普通用户登录
        user_data = {
            "mobile_phone": conf.get("test_data", "phone"),
            "pwd": conf.get("test_data", "pwd")
        }
        response2 = request(method="post", url=url, json=user_data, headers=headers)
        res2 = response2.json()
        # 提取用户id和token
        cls.user_member_id = jsonpath.jsonpath(res2, "$..id")[0]
        cls.user_token = "Bearer" + " " + jsonpath.jsonpath(res2, "$..token")[0]

        # print("管理员token:", cls.admin_token)
        # print("用户token:", cls.user_token)
        # print("用户id:", cls.user_member_id)

    def setUp(self):
        # 每条用例之前的前置条件：添加一个新的项目
        url = conf.get("env", "url") + "/loan/add"
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = self.user_token
        data = {"member_id": self.user_member_id,
                "title": "木森借钱买飞机",
                "amount": 2000,
                "loan_rate": 12.0,
                "loan_term": 3,
                "loan_date_type": 1,
                "bidding_days": 5}
        # 发送请求，添加项目
        response = request(method="post", url=url, json=data, headers=headers)
        res = response.json()
        # 提取项目的id给审核的用例使用
        self.loan_id = jsonpath.jsonpath(res, "$..id")[0]
        # print("项目id:",loan_id)

    @data(*cases)
    def test_audit(self, case):
        # 第一步：准备数据
        url = conf.get("env", "url") + case["url"]
        # 判读是否需要要替换审核通过的标id
        if "#pass_loan_id#" in case["data"]:
            # 将之前保存的审核通过的id，替换到该用例中
            case["data"] = case["data"].replace("#pass_loan_id#", str(self.pass_loan_id))

        data = eval(case["data"].replace("#loan_id#", str(self.loan_id)))

        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = self.admin_token

        method = case["method"]
        expected = eval(case["expected"])
        row = case["case_id"] + 1

        # 第二步：调用接口，获取实际结果
        response = request(url=url, method=method, json=data, headers=headers)
        res = response.json()
        # 判断是否是审核通的用例，并且审核成功
        if case["title"] == "审核通过" and res["msg"] == "OK":
            # 将执行通过的标id保存为类属性
            TestAudit.pass_loan_id = data["loan_id"]
        # 第三步：断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 对需要进行数据库校验的用例，进行校验。
            if case["check_sql"]:
                sql = case["check_sql"].replace("#loan_id#", str(self.loan_id))
                status = self.db.find_one(sql)["status"]
                self.assertEqual(expected["status"], status)
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
审核接口
前置条件：
    1、管理员登录，
    2、有待审核的项目：
        每个审核用例执行之前，去添加一个项目（普通用户添加）：添加项目之前普通用户需要登录

"""
import HTMLTestRunnerNew