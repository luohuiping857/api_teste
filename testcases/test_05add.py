"""
============================
Author:柠檬班-木森
Time:2020/3/31   20:13
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""

import os
import unittest
import jsonpath
import decimal
from library.myddt import ddt, data
from common.handle_excel import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_config import conf
from common.handle_logging import log
from common.handle_db import HandleMysql
from requests import request
from common.handle_data import EnvData,replace_data


@ddt
class TestAdd(unittest.TestCase):
    excel = HandleExcel(os.path.join(DATA_DIR, "apicases.xlsx"), "add")
    cases = excel.read_data()
    db = HandleMysql()

    @classmethod
    def setUpClass(cls):
        """用例执行的前置条件：登录"""
        # 准备登录的相关数据
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_data", "phone"),
            "pwd": conf.get("test_data", "pwd")
        }
        headers = eval(conf.get("env", "headers"))
        response = request(method="post", url=url, json=data, headers=headers)
        res = response.json()
        member_id = str(jsonpath.jsonpath(res, "$..id")[0])
        token = "Bearer" + " " + jsonpath.jsonpath(res, "$..token")[0]
        # 将提取出来的数据保存为EnvData这个类的属性（环境变量）
        setattr(EnvData, "member_id", member_id)
        setattr(EnvData, "token", token)

    @data(*cases)
    def test_add(self, case):

        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        # 替换参数中的用户id,
        # case["data"] = case["data"].replace("#member_id#", self.member_id)
        # 替换用例中的动态数据
        data = eval(replace_data(case["data"]))
        # 准备请求头
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(EnvData,"token")
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 加标之前，查询数据库中该用户标的数量
        if case["check_sql"]:
            sql = replace_data(case["check_sql"])
            start_count = self.db.find_count(sql)

        # 第二步： 发送请求获取实际结果
        response = request(url=url, method=method, json=data, headers=headers)
        res = response.json()
        print("预期结果：",expected)
        print("实际结果：",res)

        # 第三步：断言预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if case["check_sql"]:
                # 加标之后
                sql = replace_data(case["check_sql"])
                end_count = self.db.find_count(sql)
                self.assertEqual(1,end_count-start_count)
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
添加项目
前置条件：登录


数据库校验的思路：
加标之前查询 该用户对应的标数量

加标之后查询，该用对应标的数量

校验  是否有新增一条标的记录


"""