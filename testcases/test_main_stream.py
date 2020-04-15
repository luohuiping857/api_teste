
import unittest
import os
import jsonpath,random
from library.myddt import ddt, data
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from requests import request
from common.handle_logging import log
from common.handle_data import replace_data, EnvData


case_file = os.path.join(DATA_DIR, "apicases.xlsx")


@ddt
class TestMainStream(unittest.TestCase):
    excel = HandleExcel(case_file, "main_stream")
    cases = excel.read_data()

    @data(*cases)
    def test_main_stream(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + replace_data(case["url"])
        method = case["method"]
        if case["interface"] == "register":
            # 注册接口，则随机生成一个手机号码
            EnvData.mobilephone = self.random_phone()
        data = eval(replace_data(case["data"]))
        headers = eval(conf.get("env", "headers"))

        # 判断是否是登录接口，不是登录接口则需要添加token
        if case["interface"] != "login" and case["interface"] != "register":
            headers["Authorization"] = getattr(EnvData, "token_value")

        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        print("请求参数：", data)
        response = request(url=url, method=method, json=data, headers=headers)
        res = response.json()
        print("预期结果", expected)
        print("实际结果", res)
        # 发送请求后，判断是否是登陆接口
        if case["interface"].lower() == "login":
            # 提取用户id保存为类属性
            EnvData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            # 提取token,保存为类属性
            EnvData.token_value = token_type + " " + token
        # 判断是否是加标的用例，如果是的则请求标id
        if case["interface"] == "add":
            EnvData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 第三步：断言（比对预期结果和实际结果）
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertIn(expected["msg"], res["msg"])
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{}，执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))

    def random_phone(self):
        phone = "137"
        n = random.randint(100000000, 999999999)
        phone += str(n)[1:]
        return phone
