import jsonpath
from common.handle_data import EnvData
from common.handle_config import conf
from requests import request


class TestBase:

    @staticmethod
    def login():
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
