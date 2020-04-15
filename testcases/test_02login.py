"""
============================
Author:柠檬班-木森
Time:2020/3/24   21:22
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
import os
import unittest
from common.handle_excel import HandleExcel
from library.myddt import ddt, data
from common.handle_config import conf
from requests import request
from common.handle_logging import log
from common.handle_path import DATA_DIR

filename = os.path.join(DATA_DIR,"apicases.xlsx")


@ddt
class LoginTestCase(unittest.TestCase):
    excel = HandleExcel(filename, "login")
    cases = excel.read_data()

    @data(*cases)
    def test_login(self, case):
        # 第一步：准备用例数据
        # 请求方法
        method = case["method"]
        # 请求地址
        url = case["url"]
        # 请求参数
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
