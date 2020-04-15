"""
============================
Author:柠檬班-木森
Time:2020/3/24   21:44
E-mail:3247119728@qq.com
Company:湖南零檬信息技术有限公司
============================
"""
import os

# 获取项目所在的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 用例模块所在的目录路径
CASE_DIR = os.path.join(BASE_DIR, "testcases")

# 用例数据所在的目录路径
DATA_DIR = os.path.join(BASE_DIR, "data")

# 配置文件所在的目录路径
CONF_DIR = os.path.join(BASE_DIR, "conf")

# 测试报告所在的目录路径
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# 日志文件所在的目录路径
LOG_DIR = os.path.join(BASE_DIR, "logs")
