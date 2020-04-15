"""
============================
Author:柠檬班-木森
Time:2020/3/28   9:36
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
class TestRecharge(unittest.TestCase):
    excel = HandleExcel(os.path.join(DATA_DIR, "apicases.xlsx"), "recharge")
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
        setattr(EnvData,"member_id",member_id)
        setattr(EnvData,"token",token)

    @data(*cases)
    def test_recharge(self, case):

        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        # 准备用例参数
        # 替换参数中的用户id
        data = eval(replace_data(case["data"]))
        # 准备请求头
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = getattr(EnvData,"token")
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 判断该用例是否需要数据库校验，获取充值之前的账户余额
        if case["check_sql"]:
            sql = case["check_sql"].format(getattr(EnvData,"member_id"))
            start_money = self.db.find_one(sql)["leave_amount"]
            print("充值之前的金额：",start_money)

        # 第二步： 发送请求获取实际结果
        response = request(url=url, method=method, json=data, headers=headers)
        res = response.json()
        print("预期结果：",expected)
        print("实际结果：",res)

        # 判断该用例是否需要数据库校验，获取充值之后的账户余额
        if case["check_sql"]:
            sql = case["check_sql"].format(getattr(EnvData,"member_id"))
            end_money = self.db.find_one(sql)["leave_amount"]
            print("充值之后的金额：",end_money)

        # 第三步：断言预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 判断是否需要进行sql校验
            if case["check_sql"]:
                # 将充值金额转换为decimal类型（因为数据库中的金额是decimal类型的）
                recharge_money = decimal.Decimal(str(data["amount"]))
                self.assertEqual(recharge_money,end_money-start_money)
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
疑问点：
1、这行代码的意思
headers["Authorization"] = self.token
2、用户id替换的是字符串，请求的时候怎么变成数值的
case["data"].replace("#member_id#", self.member_id)


充值校验数据库怎么校验？
- 充值前后的金额变化和充值金额进行对比

充值之前查询数据库

充值之后查询数据库

断言


3.28  内容总结：
    1、用例执行的前置条件/后置条件
    2、利用setupclass方法，解决了充值之前登陆的问题
    3、充值前后的数据库校验
    
"""