


import unittest
import os
import jsonpath
from library.myddt import ddt, data
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from requests import request
from common.handle_logging import log
from common.handle_db import HandleMysql
from common.handle_data import replace_data, EnvData

case_file = os.path.join(DATA_DIR, "apicases.xlsx")

@ddt
class TestInfo(unittest.TestCase):
    excel = HandleExcel(case_file, "info")
    cases = excel.read_data()

    db = HandleMysql()

    @classmethod
    def setUpClass(cls):
        # 1、准备登录的数据
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_data", "phone"),
            "pwd": conf.get("test_data", "pwd")
        }
        headers = eval(conf.get("env", "headers"))
        # 3、发送请求，进行登录
        response = request(url=url, method="post", json=data, headers=headers)
        # 获取返回的数据
        res = response.json()
        # 3、提取token,保存为类属性
        token = jsonpath.jsonpath(res, "$..token")[0]
        token_type = jsonpath.jsonpath(res, "$..token_type")[0]
        # 将提取到的token设为类属性
        EnvData.token_value = token_type + " " + token
        # 提取用户的id，保存为类属性
        EnvData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])

    @data(*cases)
    def test_info(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + replace_data(case["url"])
        method = case["method"]
        # 替换参数中的用户id
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(EnvData,"token_value")
        # 在请求头中加入setupclass中提取出来的token
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        response = request(url=url, method=method, headers=headers)
        res = response.json()
        # 第三步：断言（比对预期结果和实际结果）
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
        except AssertionError as e:
            print("预期结果：", expected)
            print("实际结果：", res)
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{}，执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))