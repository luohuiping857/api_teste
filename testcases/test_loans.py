"""
============================
Author:柠檬班-木森
Time:2020/3/3   16:35
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""

import unittest
import os
from library.myddt import ddt, data
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from requests import request
from common.handle_logging import log
from common.handle_db import HandleMysql
from common.handle_data import replace_data

case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestLoans(unittest.TestCase):
    excel = HandleExcel(case_file, "loans")
    cases = excel.read_data()
    db = HandleMysql()
    @data(*cases)
    def test_loans(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        data = eval(replace_data(case["data"]))
        # 替换参数中的用户id
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        response = request(url=url, method=method, params=data, headers=headers)
        res = response.json()
        print(response.url)
        # 第三步：断言（比对预期结果和实际结果）
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 断言返回的数据的条数
            self.assertEqual(expected["len"],len(res["data"]))
        except AssertionError as e:
            # print("预期结果：", expected)
            # print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{}，执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
