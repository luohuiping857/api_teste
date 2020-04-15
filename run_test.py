"""
============================
Author:柠檬班-木森
Time:2020/3/17   20:18
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
import unittest
from BeautifulReport import BeautifulReport
from common.handle_logging import log
from common.handle_path import CASE_DIR,REPORT_DIR
from common.send_email import send_email


log.info("---------------开始执行测试用例-----------------------")

# 创建测试套件
suite =  unittest.TestSuite()

# 加载用例到套件
loader = unittest.TestLoader()
suite.addTest(loader.discover(CASE_DIR))

# 执行用例生成报告
bf = BeautifulReport(suite)

bf.report("注册接口",filename="report.html",report_dir=REPORT_DIR)

log.info("---------------测试用例执行完毕-----------------------")

send_email()