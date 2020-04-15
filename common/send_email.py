"""
作者：罗惠平
"""


import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from common.handle_path import REPORT_DIR
import os

"""
账号 645322089@qq.com
授权码 ncspzxcwdzmmbchf

qq邮件smtp服务器地址：smtp.qq.com
163邮件smtp服务器地址：smtp.163.com

"""
def send_email():
# 第一步 连接smtp服务器，并登录
# 连接smtp服务器
    smtp = smtplib.SMTP_SSL(host="smtp.qq.com",port=465)
    # 登录smtp服务器
    smtp.login(user="645322089@qq.com",password="ncspzxcwdzmmbchf")


    # 第二步 构造一封多组件邮件
    msg = MIMEMultipart()
    msg["Subject"] = "上课邮件001"
    msg["To"] = "747530298@qq.com"
    msg["From"] = "645322089@qq.com"

    # 构造邮件文本内容
    text = MIMEText("文本内容",_charset="utf8")
    msg.attach(text)

    # 构造邮件附件
    with open(os.path.join(REPORT_DIR,"report.html"),"rb") as f:
        content = f.read()
    report = MIMEApplication(content)
    report.add_header('content-disposition', 'attachment', filename='report.html')
    msg.attach(report)

    # 第三步 发送邮件
    smtp.send_message(msg,from_addr="645322089@qq.com",to_addrs="747530298@qq.com")